from fastapi import APIRouter, UploadFile, BackgroundTasks

from app.api.schemas.dns_entry import DNSEntry, EntryType
from app.api.schemas.project import Project
from app.db.db import db_handler
from app.db.models import Certificate
from app.db.models.project import Project as DB_Project
from app.db.models.dns_entry import DNSEntry as DB_DNSEntry
from app.tools._dns import _query, _brute_srv, _dedupe_dns_entries
from app.tools.tls_cert import fetch_cert, parse_cert


projects = APIRouter(prefix="/projects")


DNS_ENTRY_TYPES = [
    EntryType.IPv4, EntryType.IPv6,
    EntryType.CNAME,
    EntryType.MX,
    EntryType.NS,
    EntryType.SOA,
    EntryType.TXT
]


# ~~~~~~~~~~ # Utility functions # ~~~~~~~~~~ #

def _fetch_dns(domain: str):
    entries: list[DNSEntry] = []

    for entry_type in DNS_ENTRY_TYPES:
        entries.extend(_query(domain, entry_type))

    entries.extend(_brute_srv(domain))
    entries = _dedupe_dns_entries(entries)

    with db_handler.transaction() as db:
        # Delete current DB entries, insert new Records
        db.query(DB_DNSEntry).delete(synchronize_session=False)

        for entry in entries:
            db.add(DB_DNSEntry(
                type=entry.type,
                domain=entry.domain,
                value=entry.value,
                ttl=entry.ttl
            ))


def _fetch_cert(domain: str):
    # TODO: handle exceptions
    raw_cert = fetch_cert(domain)
    cert = parse_cert(raw_cert)

    with db_handler.transaction() as db:
        # Delete last certificate and replace with current one
        db.query(Certificate).delete(synchronize_session=False)
        db.add(cert)




@projects.get("/{project_id}")
def get_project(project_id: int):
    # TODO: implement auth
    pass


@projects.post("")
def create_project(
    create_project: Project,
    bg: BackgroundTasks
):
    # TODO: implement auth
    with db_handler.transaction() as db:
        db.add(DB_Project(
            name=create_project.name,
            domain=create_project.domain,
            # user_id=user.id
            user_id=1   # only for testing
        ))

    bg.add_task(_fetch_dns, create_project.domain)
    bg.add_task(_fetch_cert, create_project.domain)
    return {"success" : True}  # only for testing


@projects.patch("/{project_id}")
def update_project(project_id: int, patch_project: Project):
    # TODO: implement auth
    pass



@projects.post("/{project_id}/upload")
def upload_file(project_id: int, file: UploadFile):
    # TODO: implement auth
    pass



@projects.post("/{project_id}/analysis/start")
def start_analysis(project_id: int):
    # TODO: implement auth
    pass

