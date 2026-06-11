import os

from sqlalchemy.orm import Session

from app.api.errors import ApiError, NotFound
from app.api.schemas.responses import ProjectFull
from app.config import get_settings
from app.core.logging import get_logger
from app.db.models.certificate import Certificate
from app.db.models.dns_entry import DNSEntry
from app.db.models.endpoint import Endpoint
from app.db.models.har_file import HarFile
from app.db.models.project import Project
from app.db.models.project_har import ProjectHar
from app.db.models.technology import Technology
from app.db.models.user import User
from app.tools._dns import collect_dns
from app.tools._har import parse_har
from app.tools._ssl import fetch_certificate
from app.tools._tech import fingerprint

logger = get_logger(__name__)


def _har_dir() -> str:
    path = os.path.join(get_settings().DB_DIR, "hars")
    os.makedirs(path, exist_ok=True)
    return path


def list_projects(db: Session, user: User) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.id)
        .all()
    )


def get_owned_project(db: Session, user: User, project_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user.id)
        .first()
    )
    if project is None:
        raise NotFound("Project not found")
    return project


def create_project(db: Session, user: User, name: str, domain: str) -> Project:
    name = (name or "").strip()
    domain = (domain or "").strip()
    if not name or not domain:
        raise ApiError("Name and domain are required")

    project = Project(name=name[:30], domain=domain[:253], user_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info("Project %s created by %s", project.id, user.email)
    return project


def update_project(
    db: Session,
    user: User,
    project_id: int,
    name: str | None,
    domain: str | None,
) -> Project:
    project = get_owned_project(db, user, project_id)
    if name is not None and name.strip():
        project.name = name.strip()[:30]
    if domain is not None and domain.strip():
        project.domain = domain.strip()[:253]
    db.commit()
    db.refresh(project)
    return project


def store_har(db: Session, user: User, project_id: int, filename: str, content: bytes) -> None:
    project = get_owned_project(db, user, project_id)

    har = HarFile(filename=(filename or "upload.har")[:255])
    db.add(har)
    db.flush()  # obtain har.id

    with open(os.path.join(_har_dir(), f"{har.id}.har"), "wb") as fh:
        fh.write(content)

    db.add(ProjectHar(project_id=project.id, har_id=har.id))
    db.commit()
    logger.info("HAR %s stored for project %s", har.id, project.id)


def _replace(db: Session, model, project_id: int, rows: list) -> None:
    db.query(model).filter(model.project_id == project_id).delete()
    for row in rows:
        db.add(row)


def run_analysis(db: Session, user: User, project_id: int) -> None:
    """Run DNS, SSL, tech and endpoint analysis and persist the results (FA04/FA05)."""
    project = get_owned_project(db, user, project_id)
    domain = project.domain
    logger.info("Starting analysis for project %s (%s)", project.id, domain)

    # DNS
    dns_rows = [
        DNSEntry(project_id=project.id, type=e.type, domain=e.domain, value=e.value, ttl=e.ttl)
        for e in collect_dns(domain)
    ]
    _replace(db, DNSEntry, project.id, dns_rows)

    # SSL / TLS certificate
    cert = fetch_certificate(_hostname(domain))
    cert_rows = []
    if cert is not None:
        cert_rows = [
            Certificate(
                project_id=project.id,
                subject_domain=cert.subject_domain,
                subject_organization=cert.subject_organization,
                subject_country=cert.subject_country,
                issuer_name=cert.issuer_name,
                issuer_organization=cert.issuer_organization,
                issuer_country=cert.issuer_country,
                valid_from=cert.valid_from,
                valid_to=cert.valid_to,
                serial_number=cert.serial_number,
                public_key_type=cert.public_key_type,
                fingerprint_sha256=cert.fingerprint_sha256,
            )
        ]
    _replace(db, Certificate, project.id, cert_rows)

    # Technology fingerprinting
    tech_rows = [
        Technology(
            project_id=project.id,
            name=t.name,
            description=t.description,
            icon_url=t.icon_url,
        )
        for t in fingerprint(domain)
    ]
    _replace(db, Technology, project.id, tech_rows)

    # Endpoints from uploaded HAR files
    endpoint_rows = []
    for endpoint in _endpoints_from_hars(db, project.id):
        endpoint_rows.append(
            Endpoint(
                project_id=project.id,
                method=endpoint.method,
                path=endpoint.path,
                status=endpoint.status,
                content_type=endpoint.content_type,
            )
        )
    _replace(db, Endpoint, project.id, endpoint_rows)

    db.commit()
    logger.info(
        "Analysis done for project %s: %d dns, %d cert, %d tech, %d endpoints",
        project.id, len(dns_rows), len(cert_rows), len(tech_rows), len(endpoint_rows),
    )


def _endpoints_from_hars(db: Session, project_id: int):
    links = db.query(ProjectHar).filter(ProjectHar.project_id == project_id).all()
    seen = set()
    result = []
    for link in links:
        path = os.path.join(_har_dir(), f"{link.har_id}.har")
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            for endpoint in parse_har(fh.read()):
                key = (endpoint.method, endpoint.path)
                if key in seen:
                    continue
                seen.add(key)
                result.append(endpoint)
    return result


def _hostname(domain: str) -> str:
    domain = domain.strip()
    if "://" in domain:
        from urllib.parse import urlparse

        domain = urlparse(domain).netloc or domain
    return domain.strip("/").split("/")[0]


def build_full(project: Project) -> ProjectFull:
    # All nested schemas enable from_attributes, so a single validate maps the
    # ORM project + its relationship collections onto the response model.
    return ProjectFull.model_validate(project)
