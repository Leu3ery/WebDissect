from urllib.parse import urlparse
from functools import lru_cache
from typing import Literal
from dns.resolver import Resolver, NoAnswer, NXDOMAIN, NoNameservers
from dns.exception import Timeout

from app.api.schemas import DNSEntry, DNSEntryType
from app.tools._dns_mappings import SRV_MAPPING


@lru_cache
def get_resolver():
    resolver = Resolver()
    resolver.nameservers = ["1.1.1.1"]
    resolver.timeout = 5
    return resolver



def _dedupe_dns_entries(entries: list[DNSEntry]) -> list[DNSEntry]:
    seen: dict[tuple, DNSEntry] = {}
    for e in entries:
        key = (e.type, e.domain, e.value)
        seen.setdefault(key, e)
    return list(seen.values())




def _query(domain: str, record_type: DNSEntryType, service: str | None = None, proto: Literal["tcp", "udp"] | None = None) -> list[DNSEntry]:
    """
    Execute a DNS query

    Args:
        domain (str): Target domain
        record_type (str): DNS Record type (A,AAAA,MX,NS,TXT,SOA,SRV)
        service (str | None): Only for SRV Records; service name (e.g. minecraft)
        proto (str | None): Only for SRV Records; protocol (tcp, udp)
    """
    if record_type == DNSEntryType.SRV and (service is None or proto is None):
        raise ValueError("Missing 'service' and/or 'protocol' parameter for SRV Query")

    entries = []
    try:
        if record_type == DNSEntryType.SRV:
            new = domain if "//" in domain else f"//{domain}"
            label = f"_{service}._{proto}.{urlparse(new).netloc}"
            resp = get_resolver().resolve(label, "SRV")
        else:
            resp = get_resolver().resolve(domain, record_type)

        for rdata in resp:

            data = None
            match record_type:
                case DNSEntryType.IPv4 | DNSEntryType.IPv6:
                    data = rdata.address
                case DNSEntryType.MX:
                    data = f"Preference: {rdata.preference}, Mail Domain: {rdata.exchange}"  # 10  mail.example.com.
                case DNSEntryType.NS | DNSEntryType.CNAME:
                    data = str(rdata.target)  # ns1.example.com.
                case DNSEntryType.TXT:
                    data = b"".join(rdata.strings).decode()
                case DNSEntryType.SOA:
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
                case DNSEntryType.SRV:
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



def _brute_srv(domain: str) -> list[DNSEntry]:
    entries: list[DNSEntry] = []

    for category, data in SRV_MAPPING.items():
        for service, proto in data:
            entries.extend(_query(domain, DNSEntryType.SRV, service, proto))

    return entries

