from fastapi import APIRouter

from app.db import db_handler
from app.db.models import DNSEntry as DB_DNSEntry, Certificate as DB_Certificate
from app.api.schemas import DNSEntry, Certificate

tools = APIRouter()


@tools.get("/dns/{analysis_id}")
def get_dns_analysis(analysis_id: str) -> list[DNSEntry]:
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


