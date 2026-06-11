import asyncio
from typing import Any, Callable

from app.core.logging import get_logger
from app.db.db import SessionLocal
from app.db.models.certificate import Certificate
from app.db.models.dns_entry import DNSEntry
from app.db.models.endpoint import Endpoint
from app.db.models.path_entry import PathEntry
from app.db.models.port import Port
from app.db.models.project import Project
from app.db.models.subdomain import Subdomain
from app.db.models.technology import Technology
from app.services import projects as P
from app.services.analysis_hub import hub
from app.tools._dns import collect_dns
from app.tools._paths import enumerate_paths
from app.tools._ports import scan_ports
from app.tools._ssl import fetch_certificate
from app.tools._subdomains import enumerate_subdomains
from app.tools._tech import fingerprint

logger = get_logger(__name__)

_bg_tasks: set[asyncio.Task] = set()


def schedule(fn: Callable[[int], None], project_id: int) -> None:
    """Run a blocking analysis worker in a background thread on the event loop."""
    loop = asyncio.get_running_loop()
    hub.bind_loop(loop)
    task = loop.create_task(asyncio.to_thread(fn, project_id))
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


def _emit(project_id: int, category: str, status: str, count: int = 0, message: str = "") -> None:
    hub.publish(
        project_id,
        {"type": "progress", "category": category, "status": status, "count": count, "message": message},
    )


def _run(project_id: int, body: Callable[[Any, Project], None]) -> None:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return
        hub.publish(project_id, {"type": "start"})
        body(db, project)
    except Exception:
        logger.exception("Analysis worker failed for project %s", project_id)
        hub.publish(project_id, {"type": "error", "message": "Analysis failed"})
    finally:
        hub.publish(project_id, {"type": "complete"})
        db.close()


# --- Passive analysis (DNS, SSL, tech, subdomains, endpoints) -------------

def run_passive(project_id: int) -> None:
    def body(db, project: Project) -> None:
        domain = project.domain

        _emit(project_id, "dns", "running")
        dns = collect_dns(domain)
        P._replace(db, DNSEntry, project_id, [
            DNSEntry(project_id=project_id, type=e.type, domain=e.domain, value=e.value, ttl=e.ttl)
            for e in dns
        ])
        db.commit()
        _emit(project_id, "dns", "done", len(dns))

        _emit(project_id, "ssl", "running")
        cert = fetch_certificate(P._hostname(domain))
        cert_rows = [
            Certificate(
                project_id=project_id,
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
        ] if cert else []
        P._replace(db, Certificate, project_id, cert_rows)
        db.commit()
        _emit(project_id, "ssl", "done", len(cert_rows))

        _emit(project_id, "tech", "running")
        techs = fingerprint(domain)
        P._replace(db, Technology, project_id, [
            Technology(project_id=project_id, name=t.name, description=t.description, icon_url=t.icon_url)
            for t in techs
        ])
        db.commit()
        _emit(project_id, "tech", "done", len(techs))

        _emit(project_id, "subdomains", "running")
        subs = enumerate_subdomains(domain)
        P._replace(db, Subdomain, project_id, [
            Subdomain(project_id=project_id, name=s.name, ip=s.ip, source=s.source)
            for s in subs
        ])
        db.commit()
        _emit(project_id, "subdomains", "done", len(subs))

        _emit(project_id, "endpoints", "running")
        eps = list(P._endpoints_from_hars(db, project_id))
        P._replace(db, Endpoint, project_id, [
            Endpoint(project_id=project_id, method=e.method, path=e.path, status=e.status, content_type=e.content_type)
            for e in eps
        ])
        db.commit()
        _emit(project_id, "endpoints", "done", len(eps))

    _run(project_id, body)


# --- Active scans (opt-in) ------------------------------------------------

def run_port_scan(project_id: int) -> None:
    def body(db, project: Project) -> None:
        _emit(project_id, "ports", "running")
        ports = scan_ports(
            project.domain,
            on_progress=lambda done, total: _emit(project_id, "ports", "running", 0, f"{done}/{total}"),
        )
        P._replace(db, Port, project_id, [
            Port(project_id=project_id, port=p.port, protocol=p.protocol, state=p.state,
                 service=p.service, version=p.version, banner=p.banner)
            for p in ports
        ])
        db.commit()
        _emit(project_id, "ports", "done", len(ports))

    _run(project_id, body)


def run_path_scan(project_id: int) -> None:
    def body(db, project: Project) -> None:
        _emit(project_id, "paths", "running")
        paths = enumerate_paths(
            project.domain,
            on_progress=lambda done, total: _emit(project_id, "paths", "running", 0, f"{done}/{total}"),
        )
        P._replace(db, PathEntry, project_id, [
            PathEntry(project_id=project_id, path=e.path, status=e.status,
                      content_type=e.content_type, length=e.length)
            for e in paths
        ])
        db.commit()
        _emit(project_id, "paths", "done", len(paths))

    _run(project_id, body)
