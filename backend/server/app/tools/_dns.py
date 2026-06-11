from urllib.parse import urlparse
from functools import lru_cache
import dns
from dns.resolver import NoAnswer, NXDOMAIN, NoNameservers
from dns.exception import Timeout
from typing import Literal

from app.api.schemas.dns_entry import DNSEntry, EntryType


@lru_cache
def get_resolver():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["1.1.1.1"]
    resolver.timeout = 5
    return resolver


# TODO: CNAME / PTR
def _query(domain: str, record_type: EntryType, service: str | None = None, proto: Literal["tcp", "udp"] | None = None) -> list[DNSEntry]:
    """
    Execute a DNS query

    Args:
        domain (str): Target domain
        record_type (str): DNS Record type (A,AAAA,MX,NS,TXT,SOA,SRV)
        service (str | None): Only for SRV Records; service name (e.g. minecraft)
        proto (str | None): Only for SRV Records; protocol (tcp, udp)
    """
    if record_type == EntryType.SRV and (service is None or proto is None):
        raise ValueError("Missing 'service' and/or 'protocol' parameter for SRV Query")

    entries = []
    try:
        if record_type == EntryType.SRV:
            if "://" not in domain:
                domain = "//" + domain
            label = f"_{service}._{proto}._{urlparse(domain).netloc}"
            resp = get_resolver().resolve(label, "SRV")
        else:
            resp = get_resolver().resolve(domain, record_type)

        for rdata in resp:

            data = None
            match record_type:
                case EntryType.IPv4 | EntryType.IPv6:
                    data = rdata.address
                case EntryType.MX:
                    data = f"Preference: {rdata.preference}, Mail Domain: {rdata.exchange}"  # 10  mail.example.com.
                case EntryType.NS:
                    data = str(rdata.target)  # ns1.example.com.
                case EntryType.TXT:
                    data = b"".join(rdata.strings).decode()
                case EntryType.SOA:
                    if resp:
                        soa = resp[0]
                        master_ns = soa.mname
                        responsible_person_email = soa.rname
                        zone_version_number = soa.serial
                        version_number_refresh = soa.refresh
                        refresh_check_retry = soa.retry
                        expire_limit = soa.expire
                        negative_response_ttl = soa.minimum
                        data = f"Master NS: {master_ns}, Email: {responsible_person_email}, Zone Version Number: {zone_version_number} (refresh: {version_number_refresh}, refresh check retry: {refresh_check_retry}), expire: {expire_limit}, negative_response_ttl: {negative_response_ttl}"
                    else:
                        data = None
                case EntryType.SRV:
                    data = f"Priority: {rdata.priority}, Weight: {rdata.weight}, Port: {rdata.port}, Host: {rdata.target}"


            entries.append(DNSEntry(
                type=record_type,
                domain=domain,
                ttl=resp.rrset.ttl,
                value=data
            ))
    except (NoAnswer, NXDOMAIN, NoNameservers, Timeout):
        return []
    return entries




_DEFAULT_TYPES = [
    EntryType.IPv4,
    EntryType.IPv6,
    EntryType.MX,
    EntryType.NS,
    EntryType.TXT,
    EntryType.SOA,
]


def _hostname(domain: str) -> str:
    if "://" in domain:
        domain = urlparse(domain).netloc or domain
    return domain.strip().strip("/")


def collect_dns(domain: str, types: list[EntryType] | None = None) -> list[DNSEntry]:
    """Query a domain for the common DNS record types and return all entries."""
    host = _hostname(domain)
    entries: list[DNSEntry] = []
    for record_type in (types or _DEFAULT_TYPES):
        try:
            entries.extend(_query(domain=host, record_type=record_type))
        except Exception:
            # One failing record type must not abort the whole lookup.
            continue
    return entries


if __name__ == "__main__":
    for type_ in [EntryType.IPv4, EntryType.IPv6, EntryType.MX, EntryType.NS, EntryType.TXT, EntryType.SOA]:
        entries = _query(domain="lernkaro.at", record_type=type_)
        for entry in entries:
            print(entry.type.ljust(5), entry.value)

    entries = _query(domain="lernkaro.at", record_type=EntryType.SRV, service="minecraft", proto="tcp")
    for entry in entries:
        print(entry.type.ljust(5), entry.value)


