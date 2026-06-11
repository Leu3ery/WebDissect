from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks

from app.api.schemas.dns_entry import DNSEntry, EntryType
from app.api.schemas.project import Project
from app.db.db import get_db, session_scope
from app.db.models.project import Project as DB_Project
from app.db.models.dns_entry import DNSEntry as DB_DNSEntry
from app.tools._dns import _query, _brute_srv, _dedupe_dns_entries

projects = APIRouter(prefix="/projects")



# ~~~~~~~~~~ # Utility functions # ~~~~~~~~~~ #

def _fetch_dns(domain: str):
    entries: list[DNSEntry] = []

    for entry_type in [
        EntryType.IPv4, EntryType.IPv6,
        EntryType.CNAME,
        EntryType.MX,
        EntryType.NS,
        EntryType.SOA,
        EntryType.TXT
    ]:
        entries.extend(_query(domain, entry_type))

    entries.extend(_brute_srv(domain))
    entries = _dedupe_dns_entries(entries)

    with session_scope() as db:
        # Delete current DB entries, insert new Records
        db.query(DB_DNSEntry).delete(synchronize_session=False)
        db.commit()

        for entry in entries:
            db.add(DB_DNSEntry(
                type=entry.type,
                domain=entry.domain,
                value=entry.value,
                ttl=entry.ttl
            ))
        db.commit()



@projects.get("/{project_id}")
def get_project(project_id: int, db = Depends(get_db)):
    pass


@projects.post("")
def create_project(
    create_project: Project,
    bg: BackgroundTasks,
    db = Depends(get_db),
):
    # TODO: catch pydantic ValidationError
    db.add(DB_Project(
        name=create_project.name,
        domain=create_project.domain,
        # user_id=user.id
        user_id=1   # only for testing
    ))
    db.commit()

    bg.add_task(_fetch_dns, create_project.domain)
    # bg.add_task(_fetch_certs, create_project.domain)
    return {"success" : True}


@projects.patch("/{project_id}")
def update_project(project_id: int, patch_project: Project, db = Depends(get_db)):
    pass



@projects.post("/{project_id}/upload")
def upload_file(project_id: int, file: UploadFile, db = Depends(get_db)):
    pass



@projects.post("/{project_id}/analysis/start")
def start_analysis(project_id: int, db = Depends(get_db)):
    pass

