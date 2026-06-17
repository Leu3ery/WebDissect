from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException

from app.api.schemas import BaseResponse, AnalysisStartData
from app.api.schemas import Project, DNSEntry, DNSEntryType
from app.api.schemas._responses import AnalysisStart
from app.db import db_handler
from app.db.models import Certificate, Analysis, Project as DB_Project, DNSEntry as DB_DNSEntry
from app.tools._dns import _query, _brute_srv, _dedupe_dns_entries
from app.tools.tls_cert import fetch_cert, parse_cert


projects = APIRouter(prefix="/projects")


DNS_ENTRY_TYPES = [
    DNSEntryType.IPv4, DNSEntryType.IPv6,
    DNSEntryType.CNAME,
    DNSEntryType.MX,
    DNSEntryType.NS,
    DNSEntryType.SOA,
    DNSEntryType.TXT
]


# ~~~~~~~~~~ # Utility functions # ~~~~~~~~~~ #

def _fetch_dns(domain: str, analysis_id: int):
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
                ttl=entry.ttl,
                analysis_id=analysis_id
            ))


    # Mark DNS Analysis as completed
    with db_handler.transaction() as db:
        db.get(Analysis, analysis_id).is_dns_analysis_completed = True


def _fetch_cert(domain: str, analysis_id: int):
    # TODO: handle exceptions
    raw_cert = fetch_cert(domain)
    cert = parse_cert(raw_cert)
    cert.analysis_id = analysis_id

    with db_handler.transaction() as db:
        # Delete last certificate and replace with current one
        db.query(Certificate).delete(synchronize_session=False)
        db.add(cert)


    # Mark Certificate Analysis as completed
    with db_handler.transaction() as db:
        db.get(Analysis, analysis_id).is_certificate_analysis_completed = True



@projects.get("/{project_id}")
def get_project(project_id: int):
    # TODO: implement auth
    pass


@projects.post("")
def create_project(create_project: Project):
    # TODO: implement auth
    project_id = None
    with db_handler.transaction() as db:
        project = DB_Project(
            name=create_project.name,
            domain=create_project.domain,
            # user_id=user.id
            user_id=1   # only for testing
        )
        db.add(project)
        db.flush()
        project_id = project.id

    return BaseResponse(data={"projectId" : project_id})  # only for testing


@projects.patch("/{project_id}")
def update_project(project_id: int, patch_project: Project):
    # TODO: implement auth
    with db_handler.transaction() as db:
        proj = db.get(DB_Project, project_id)
        proj.domain = patch_project.domain
        proj.name = patch_project.name

    return BaseResponse(data={})



@projects.post("/{project_id}/upload")
def upload_file(project_id: int, file: UploadFile):
    # TODO: implement auth
    pass



@projects.post("/{project_id}/analysis/start", response_model=BaseResponse[AnalysisStartData])
def start_analysis(project_id: int, bg: BackgroundTasks):
    # TODO: implement auth

    with db_handler.transaction() as db:
        project = db.get(DB_Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_domain = project.domain


    # Create new analysis in DB
    with db_handler.transaction() as db:
        analysis = Analysis(
            project_id=project_id
        )
        db.add(analysis)
        db.flush()   # required so the database generates the PK
        analysis_id = analysis.id


    # Start analysis and return analysis id
    bg.add_task(_fetch_dns, project_domain, analysis_id)
    bg.add_task(_fetch_cert, project_domain, analysis_id)
    return AnalysisStart(data=AnalysisStartData(analysis_id=analysis_id))

