import json
from urllib.parse import urlparse

from app.api.schemas.endpoint import Endpoint
from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_har(raw: bytes | str) -> list[Endpoint]:
    """Extract unique HTTP endpoints from a HAR (HTTP Archive) file."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.info("Invalid HAR file: %s", exc)
        return []

    entries = (data.get("log") or {}).get("entries") or []
    seen: set[tuple[str, str]] = set()
    endpoints: list[Endpoint] = []

    for entry in entries:
        request = entry.get("request") or {}
        response = entry.get("response") or {}

        method = (request.get("method") or "").upper()
        url = request.get("url") or ""
        if not method or not url:
            continue

        parsed = urlparse(url)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        path = path[:2048]

        status = response.get("status") or 0
        if not (100 < status < 600):
            # Skip failed / aborted requests (status 0) which violate the
            # endpoint constraint and carry no useful info.
            continue

        content_type = ((response.get("content") or {}).get("mimeType") or "").split(";")[0]
        content_type = content_type or "unknown"

        key = (method, path)
        if key in seen:
            continue
        seen.add(key)

        endpoints.append(
            Endpoint(
                method=method,
                path=path,
                status=status,
                content_type=content_type[:100],
            )
        )

    return endpoints
