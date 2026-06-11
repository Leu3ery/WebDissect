import json
import socket
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.api.schemas.subdomain import Subdomain
from app.core.logging import get_logger

logger = get_logger(__name__)

_MAX_RESOLVE = 200


def hostname(domain: str) -> str:
    domain = (domain or "").strip()
    if "://" in domain:
        from urllib.parse import urlparse

        domain = urlparse(domain).netloc or domain
    return domain.strip("/").split("/")[0].lower()


def parse_crtsh(json_text: str, domain: str) -> list[str]:
    """Extract unique subdomain names from a crt.sh JSON response (pure)."""
    domain = domain.lower().lstrip(".")
    try:
        rows = json.loads(json_text)
    except (json.JSONDecodeError, TypeError):
        return []

    names: set[str] = set()
    for row in rows:
        value = (row.get("name_value") or "") + "\n" + (row.get("common_name") or "")
        for raw in value.splitlines():
            name = raw.strip().lower().lstrip("*.")
            if not name:
                continue
            if name == domain or name.endswith("." + domain):
                names.add(name)
    return sorted(names)


def from_crtsh(domain: str, timeout: int = 15) -> list[str]:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "WebDissect"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        logger.info("crt.sh lookup failed for %s: %s", domain, exc)
        return []
    return parse_crtsh(text, domain)


def resolve_ip(host: str) -> str | None:
    try:
        return socket.gethostbyname(host)
    except (socket.gaierror, socket.timeout, OSError):
        return None


def enumerate_subdomains(
    domain: str,
    on_progress: Callable[[int], None] | None = None,
) -> list[Subdomain]:
    """Discover subdomains via crt.sh and resolve their IPs."""
    host = hostname(domain)
    names = from_crtsh(host)[:_MAX_RESOLVE]
    results: list[Subdomain] = []

    with ThreadPoolExecutor(max_workers=30) as pool:
        for name, ip in zip(names, pool.map(resolve_ip, names)):
            results.append(Subdomain(name=name, ip=ip or "", source="crt.sh"))
            if on_progress:
                on_progress(len(results))
    return results
