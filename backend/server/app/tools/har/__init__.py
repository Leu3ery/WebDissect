import json
from pathlib import Path
from urllib.parse import urlsplit

from app.api.schemas import Endpoint


def validate_har(path: Path) -> int:
    """
    Validate a HAR file.

    Args:
        path (Path): Path to the HAR file.

    Returns:
        int: Number of entries in the file.

    Raises:
        ValueError: If the HAR file is invalid.
    """
    with path.open("rb") as f:
        data = json.load(f)
    log = data.get("log")
    if not isinstance(log, dict) or "entries" not in log:
        raise ValueError("missing log.entries - not a HAR")
    v = log.get("version")
    if v not in {"1.1", "1.2", None}:
        raise ValueError(f"unsupported HAR version {v}")
    return len(data.get("log", {}).get("entries", []))



def parse_hars(hars: list[dict], analysis_id: int) -> list[Endpoint]:
    seen: dict[tuple[str, str], Endpoint] = {}

    for har in hars:
        for entry in har.get("log", {}).get("entries", []):
            req = entry.get("request", {})
            res = entry.get("response", {})

            method = req.get("method", "").upper()
            path = urlsplit(req.get("url", "")).path or "/"  # strip scheme/host/query
            key = (method, path)
            if not method or key in seen:  # first occurrence wins; flip with seen[key] = ... to keep last
                continue

            content_type = res.get("content", {}).get("mimeType", "")
            content_type = content_type.split(";")[0].strip()  # drop "; charset=utf-8"

            seen[key] = Endpoint(
                analysis_id=analysis_id,
                method=method,
                path=path,
                status=res.get("status", 0),
                content_type=content_type,
            )

    return list(seen.values())