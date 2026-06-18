import json
from pathlib import Path


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
