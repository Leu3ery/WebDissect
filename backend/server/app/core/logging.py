import logging
import sys

from app.config import get_settings

_configured = False


def setup_logging() -> None:
    """Configure root logging once (FA06 - logging)."""
    global _configured
    if _configured:
        return

    level = logging.DEBUG if get_settings().ENV == "development" else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
