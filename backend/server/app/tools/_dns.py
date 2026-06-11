from urllib.parse import urlparse
from functools import lru_cache
from typing import Literal
from dns.resolver import Resolver, NoAnswer, NXDOMAIN, NoNameservers
from dns.exception import Timeout

from app.api.schemas.dns_entry import DNSEntry, EntryType


@lru_cache
def get_resolver():
    resolver = Resolver()
    resolver.nameservers = ["1.1.1.1"]
    resolver.timeout = 5
    return resolver


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
            new = domain if "//" in domain else f"//{domain}"
            label = f"_{service}._{proto}.{urlparse(new).netloc}"
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
                case EntryType.NS | EntryType.CNAME:
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


