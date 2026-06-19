from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException
from uuid import uuid4
from pathlib import Path
import json

from app.api.schemas import PatchProject
from app.api.schemas import BaseResponse, CreateProject, AnalysisStart, ProjectWithAnalysisId, FileUpload
from app.api.schemas import Project, DNSEntry, DNSEntryType, Endpoint
from app.config import get_settings
from app.db import db_handler
from app.db.models import Certificate as DB_Certificate, Analysis as DB_Analysis, Project as DB_Project, DNSEntry as DB_DNSEntry, HarFile as DB_HarFile, Endpoint as DB_Endpoint
from app.tools.har import validate_har, parse_hars
from app.tools._dns import _query, _brute_srv, _dedupe_dns_entries
from app.tools.tls_cert import fetch_cert, parse_cert


# ~~~~~~~~~~ # HAR upload config # ~~~~~~~~~~ #
MAX_HAR_SIZE = 50 * 1024 * 1024  # 50 MiB
CHUNK_SIZE = 1024 * 1024
UPLOAD_DIR = Path(f"/app/storage/{get_settings().HAR_STORAGE_DIR}")


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
        # Replace only THIS analysis' entries, not every project's.
        db.query(DB_DNSEntry).where(DB_DNSEntry.analysis_id == analysis_id).delete(synchronize_session=False)

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
        db.get(DB_Analysis, analysis_id).is_dns_analysis_completed = True


def _fetch_cert(domain: str, analysis_id: int):
    # TODO: handle exceptions
    raw_cert = fetch_cert(domain)
    cert = parse_cert(raw_cert)
    cert.analysis_id = analysis_id

    with db_handler.transaction() as db:
        # Replace only THIS analysis' certificate, not every project's.
        db.query(DB_Certificate).where(DB_Certificate.analysis_id == analysis_id).delete(synchronize_session=False)
        db.add(cert)

    # TODO: remove
    # Mark Certificate Analysis as completed
    with db_handler.transaction() as db:
        db.get(DB_Analysis, analysis_id).is_certificate_analysis_completed = True


def _analyze_har(project_id: int, analysis_id: int):
    with db_handler.transaction() as db:
        har_files = db.query(DB_HarFile).where(DB_HarFile.project_id == project_id).all()
        filenames: list[str] = [f.filename for f in har_files]

    har_data = []
    for f in filenames:
        file = UPLOAD_DIR / f
        try:
            text = file.read_text()
            har_data.append(json.loads(text))
        except Exception as e:
            print("ERROR parsing HAR file:")
            print(e)
            continue

    endpoints: list[Endpoint] = parse_hars(har_data, analysis_id)

    with db_handler.transaction() as db:
        db.query(DB_Endpoint).where(DB_Endpoint.analysis_id == analysis_id).delete(synchronize_session=False)

        for endpoint in endpoints:
            e = DB_Endpoint(
                analysis_id=analysis_id,
                method=endpoint.method,
                path=endpoint.path,
                status=endpoint.status,
                content_type=endpoint.content_type
            )
            db.add(e)




@projects.get("", response_model=BaseResponse[list[ProjectWithAnalysisId]])
def get_projects():
    # TODO: implement auth

    projects = []
    with db_handler.transaction() as db:
        for p in db.query(DB_Project).all():
            p = Project.model_validate(p)

            latest_analysis = db.query(DB_Analysis).where(DB_Analysis.project_id == p.id).order_by(DB_Analysis.started_at.desc()).first()
            id_ = latest_analysis.id if latest_analysis else None

            projects.append(ProjectWithAnalysisId(
                project=p,
                analysis_id=id_
            ))

    return BaseResponse.ok(projects)



@projects.post("", response_model=BaseResponse[CreateProject])
def create_project(create_project: Project):
    # TODO: implement auth
    project_id = None
    with db_handler.transaction() as db:
        project = DB_Project(
            name=create_project.name,
            domain=create_project.domain,
        )
        db.add(project)
        db.flush()
        project_id = project.id

    return BaseResponse.ok(CreateProject(project_id=project_id))



@projects.patch("/{project_id}", response_model=BaseResponse[None])
def update_project(project_id: int, patch_project: PatchProject):
    # TODO: implement auth

    with db_handler.transaction() as db:
        proj = db.get(DB_Project, project_id)
        if patch_project.domain:
            proj.domain = patch_project.domain
        if patch_project.name:
            proj.name = patch_project.name

    return BaseResponse.ok()



@projects.post("/{project_id}/upload", response_model=BaseResponse[FileUpload], operation_id="upload_har")
def upload_file(project_id: int, file: UploadFile):
    # TODO: implement auth

    # ~~~~~~~~~~ # Validate Upload # ~~~~~~~~~~ #
    with db_handler.transaction() as db:
        proj = db.get(DB_Project, project_id)
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename or not file.filename.endswith(".har"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .har files allowed.")

    if file.size is not None and file.size > MAX_HAR_SIZE:
        raise HTTPException(status_code=413, detail="File too large")


    # ~~~~~~~~~~ # Save har file # ~~~~~~~~~~ #
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{project_id}_{uuid4().hex}.har"
    dest = UPLOAD_DIR / filename

    written = 0
    try:
        with dest.open("wb") as out:
            while chunk := file.file.read(CHUNK_SIZE):  # sync read; cap enforced as we go
                written += len(chunk)
                if written > MAX_HAR_SIZE:
                    raise HTTPException(status_code=413, detail="File too large")
                out.write(chunk)

            entry_count = validate_har(dest)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):  # catch ValueError from validate_har
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Not a valid HAR file")
    except Exception:
        dest.unlink(missing_ok=True)  # cap hit, disk error, etc. — don't leave a bad file behind
        raise
    finally:
        file.file.close()


    # ~~~~~~~~~~ # Save har to DB # ~~~~~~~~~~ #
    with db_handler.transaction() as db:
        har_file = DB_HarFile(
            project_id=project_id,
            filename=filename
        )
        db.add(har_file)

    return BaseResponse.ok(FileUpload(entry_count=entry_count))



@projects.post("/{project_id}/analysis/start", response_model=BaseResponse[AnalysisStart])
def start_analysis(project_id: int, bg: BackgroundTasks):
    # TODO: implement auth

    with db_handler.transaction() as db:
        project = db.get(DB_Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_domain = project.domain


    # Create new analysis in DB
    with db_handler.transaction() as db:
        analysis = DB_Analysis(
            project_id=project_id
        )
        db.add(analysis)
        db.flush()   # required so the database generates the PK
        analysis_id = analysis.id


    # Start analysis and return analysis id
    bg.add_task(_fetch_dns, project_domain, analysis_id)
    bg.add_task(_fetch_cert, project_domain, analysis_id)
    bg.add_task(_analyze_har, project_id, analysis_id)
    return BaseResponse.ok(AnalysisStart(analysis_id=analysis_id))



@projects.delete("/{project_id}", response_model=BaseResponse[None])
def delete_project(project_id: int):
    with db_handler.transaction() as db:
        project = db.get(DB_Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        analyses = db.query(DB_Analysis).filter(DB_Analysis.project_id == project_id).all()
        for analysis in analyses:
            db.query(DB_Endpoint).filter(DB_Endpoint.analysis_id == analysis.id).delete(synchronize_session=False)
            db.query(DB_DNSEntry).filter(DB_DNSEntry.analysis_id == analysis.id).delete(synchronize_session=False)
            db.query(DB_Certificate).filter(DB_Certificate.analysis_id == analysis.id).delete(synchronize_session=False)
            db.delete(analysis)

        har_files = db.query(DB_HarFile).filter(DB_HarFile.project_id == project_id).all()
        for har_file in har_files:
            (UPLOAD_DIR / har_file.filename).unlink(missing_ok=True)
            db.delete(har_file)

        db.delete(project)

    return BaseResponse.ok()


