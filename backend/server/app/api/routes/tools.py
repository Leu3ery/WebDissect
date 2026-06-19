from fastapi import APIRouter

from app.db import db_handler
from app.db.models import DNSEntry as DB_DNSEntry, Certificate as DB_Certificate, Endpoint as DB_Endpoint
from app.api.schemas import DNSEntry, Certificate, Endpoint

tools = APIRouter()


@tools.get("/dns/{analysis_id}", response_model=list[DNSEntry])
def get_dns_analysis(analysis_id: str):
    with db_handler.transaction() as db:
        entries = db.query(DB_DNSEntry).where(DB_DNSEntry.analysis_id == analysis_id).all()
        return [DNSEntry.model_validate(entry) for entry in entries]


@tools.get("/tls/{analysis_id}")
def get_tls_analysis(analysis_id: str) -> Certificate | None:
    with db_handler.transaction() as db:
        res = db.query(DB_Certificate).where(DB_Certificate.analysis_id == analysis_id).first()  # only returns one result anyway if it works as intended
        if res:
            return Certificate.model_validate(res)
        return None


@tools.get("/har/{analysis_id}", response_model=list[Endpoint])
def get_har_endpoints(analysis_id: str):
    with db_handler.transaction() as db:
        res = db.query(DB_Endpoint).where(DB_Endpoint.analysis_id == analysis_id).all()
        if res:
            return [Endpoint.model_validate(e) for e in res]
        return []


