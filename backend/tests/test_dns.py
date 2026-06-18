"""
Tests for app.api.services.dns._query

Strategy: get_resolver() is replaced with a fake so no real DNS is hit.
Each test feeds a FakeAnswer (mimicking dnspython's Answer object) and asserts
on the parsed DNSEntry. DNS failure modes are simulated via side_effect.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from dns.resolver import NoAnswer, NXDOMAIN, NoNameservers
from dns.exception import Timeout

import app.tools._dns as dns_service
from app.tools._dns import _query
from app.api.schemas.dns_entry import DNSEntry, DNSEntryType



# --------------------------------------------------------------------------- #
# Fakes / fixtures
# --------------------------------------------------------------------------- #
class FakeAnswer:
    """
    Stand-in for dns.resolver.Answer. Supports the exact surface _query touches:
    iteration (for rdata in resp), indexing (resp[0] in SOA), truthiness
    (if resp), and resp.rrset.ttl.
    """
    def __init__(self, rdata_list, ttl=300):
        self._rdata = list(rdata_list)
        self.rrset = SimpleNamespace(ttl=ttl)

    def __iter__(self):
        return iter(self._rdata)

    def __getitem__(self, idx):
        return self._rdata[idx]

    def __len__(self):
        return len(self._rdata)

    def __bool__(self):
        return bool(self._rdata)


@pytest.fixture
def resolver(monkeypatch):
    """Patch get_resolver so _query uses a controllable MagicMock resolver."""
    mock = MagicMock(name="resolver")
    monkeypatch.setattr(dns_service, "get_resolver", lambda: mock)
    return mock


# Convenience rdata builders ------------------------------------------------- #
def a_rdata(address):
    return SimpleNamespace(address=address)


def mx_rdata(preference, exchange):
    return SimpleNamespace(preference=preference, exchange=exchange)


def target_rdata(target):
    return SimpleNamespace(target=target)


def txt_rdata(*chunks):
    return SimpleNamespace(strings=list(chunks))


def soa_rdata():
    return SimpleNamespace(
        mname="ns1.example.com.",
        rname="hostmaster.example.com.",
        serial=2024010101,
        refresh=7200,
        retry=3600,
        expire=1209600,
        minimum=300,
    )


def srv_rdata(priority, weight, port, target):
    return SimpleNamespace(priority=priority, weight=weight, port=port, target=target)


# --------------------------------------------------------------------------- #
# Guard clause (runs before any resolver call)
# --------------------------------------------------------------------------- #
class TestSrvValidation:
    def test_srv_without_service_raises(self):
        with pytest.raises(ValueError):
            _query("example.com", DNSEntryType.SRV, service=None, proto="tcp")

    def test_srv_without_proto_raises(self):
        with pytest.raises(ValueError):
            _query("example.com", DNSEntryType.SRV, service="minecraft", proto=None)

    def test_srv_without_both_raises(self):
        with pytest.raises(ValueError):
            _query("example.com", DNSEntryType.SRV)


# --------------------------------------------------------------------------- #
# Per-record-type parsing
# --------------------------------------------------------------------------- #
class TestRecordParsing:
    @pytest.mark.parametrize("rtype", [DNSEntryType.IPv4, DNSEntryType.IPv6])
    def test_address_records(self, resolver, rtype):
        resolver.resolve.return_value = FakeAnswer([a_rdata("93.184.216.34")], ttl=120)
        result = _query("example.com", rtype)

        assert len(result) == 1
        entry = result[0]
        assert isinstance(entry, DNSEntry)
        assert entry.type == rtype
        assert entry.domain == "example.com"
        assert entry.value == "93.184.216.34"
        assert entry.ttl == 120
        resolver.resolve.assert_called_once_with("example.com", rtype)

    def test_multiple_records_produce_multiple_entries(self, resolver):
        resolver.resolve.return_value = FakeAnswer(
            [a_rdata("1.1.1.1"), a_rdata("8.8.8.8")]
        )
        result = _query("example.com", DNSEntryType.IPv4)
        assert [e.value for e in result] == ["1.1.1.1", "8.8.8.8"]

    def test_mx_record(self, resolver):
        resolver.resolve.return_value = FakeAnswer([mx_rdata(10, "mail.example.com.")])
        result = _query("example.com", DNSEntryType.MX)
        assert result[0].value == "Preference: 10, Mail Domain: mail.example.com."

    def test_ns_record(self, resolver):
        resolver.resolve.return_value = FakeAnswer([target_rdata("ns1.example.com.")])
        result = _query("example.com", DNSEntryType.NS)
        assert result[0].value == "ns1.example.com."

    def test_cname_record(self, resolver):
        resolver.resolve.return_value = FakeAnswer([target_rdata("alias.example.com.")])
        result = _query("www.example.com", DNSEntryType.CNAME)
        assert result[0].value == "alias.example.com."

    def test_txt_record_joins_and_decodes(self, resolver):
        # TXT values arrive as a sequence of byte chunks that must be concatenated.
        resolver.resolve.return_value = FakeAnswer(
            [txt_rdata(b"v=spf1 ", b"include:_spf.example.com ~all")]
        )
        result = _query("example.com", DNSEntryType.TXT)
        assert result[0].value == "v=spf1 include:_spf.example.com ~all"

    def test_soa_record(self, resolver):
        resolver.resolve.return_value = FakeAnswer([soa_rdata()], ttl=86400)
        result = _query("example.com", DNSEntryType.SOA)

        expected = (
            "Master NS: ns1.example.com., Email: hostmaster.example.com., "
            "Zone Version Number: 2024010101 (refresh: 7200, refresh check retry: 3600), "
            "expire: 1209600, negative_response_ttl: 300"
        )
        assert result[0].value == expected
        assert result[0].ttl == 86400


# --------------------------------------------------------------------------- #
# SRV: label construction + parsing
# --------------------------------------------------------------------------- #
class TestSrv:
    def test_srv_builds_underscore_label_and_parses(self, resolver):
        resolver.resolve.return_value = FakeAnswer(
            [srv_rdata(10, 5, 25565, "mc.example.com.")]
        )
        result = _query("example.com", DNSEntryType.SRV, service="minecraft", proto="tcp")

        # Correct DNS label is built for the lookup...
        resolver.resolve.assert_called_once_with("_minecraft._tcp.example.com", "SRV")
        # ...the parsed value is formatted...
        assert result[0].value == "Priority: 10, Weight: 5, Port: 25565, Host: mc.example.com."
        # ...and the stored domain is the original input, not the label.
        assert result[0].domain == "example.com"

    def test_srv_strips_scheme_from_domain(self, resolver):
        resolver.resolve.return_value = FakeAnswer(
            [srv_rdata(0, 0, 443, "svc.example.com.")]
        )
        _query("https://example.com", DNSEntryType.SRV, service="sip", proto="udp")
        resolver.resolve.assert_called_once_with("_sip._udp.example.com", "SRV")


# --------------------------------------------------------------------------- #
# Failure modes -> empty list
# --------------------------------------------------------------------------- #
class TestErrorHandling:
    @pytest.mark.parametrize("exc", [NoAnswer, NXDOMAIN, NoNameservers, Timeout])
    def test_swallowed_dns_errors_return_empty(self, resolver, exc):
        resolver.resolve.side_effect = exc
        assert _query("example.com", DNSEntryType.IPv4) == []

    def test_unexpected_error_is_not_swallowed(self, resolver):
        # Only the four DNS exceptions are caught; anything else should propagate.
        resolver.resolve.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            _query("example.com", DNSEntryType.IPv4)


