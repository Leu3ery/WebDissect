from backend.server.app.tools._dns import _query
from backend.server.app.api.schemas.dns_entry import EntryType



if __name__ == "__main__":
    for type_ in [EntryType.IPv4, EntryType.IPv6, EntryType.MX, EntryType.NS, EntryType.TXT, EntryType.SOA]:
        entries = _query(domain="google.com", record_type=type_)
        for entry in entries:
            print(entry.type.ljust(5), entry.value)

    entries = _query(domain="google.com", record_type=EntryType.SRV, service="minecraft", proto="tcp")
    for entry in entries:
        print(entry.type.ljust(5), entry.value)



