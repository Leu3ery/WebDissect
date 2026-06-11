import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.api.schemas.path_entry import PathEntry
from app.core.logging import get_logger

logger = get_logger(__name__)

# Common paths worth probing on an unknown web app.
WORDLIST: list[str] = [
    "admin", "administrator", "login", "logout", "register", "signup", "signin",
    "dashboard", "account", "profile", "user", "users", "settings", "config",
    "api", "api/v1", "api/v2", "graphql", "swagger", "swagger-ui", "openapi.json",
    "docs", "redoc", "health", "healthz", "status", "metrics", "version",
    "robots.txt", "sitemap.xml", "humans.txt", ".well-known/security.txt",
    ".git/HEAD", ".git/config", ".env", ".env.local", "config.json", "config.php",
    "wp-admin", "wp-login.php", "wp-json", "xmlrpc.php", "wp-content",
    "phpmyadmin", "adminer.php", "server-status", "server-info",
    "backup", "backups", "backup.zip", "backup.sql", "db.sql", "dump.sql",
    "upload", "uploads", "files", "download", "downloads", "static", "assets",
    "media", "images", "img", "css", "js", "fonts", "tmp", "temp", "cache",
    "test", "tests", "debug", "dev", "staging", "old", "new", "beta",
    "private", "internal", "secret", "secrets", "hidden", "data",
    "cgi-bin", "console", "shell", "cmd", "info.php", "phpinfo.php",
    "index.php", "index.html", "home", "about", "contact", "search",
    "cart", "checkout", "order", "orders", "payment", "invoice",
    "rss", "feed", "atom.xml", "favicon.ico", "manifest.json",
    "actuator", "actuator/health", "actuator/env", "jenkins", "grafana",
    "kibana", "prometheus", ".DS_Store", "web.config", "crossdomain.xml",
]


def is_interesting(status: int) -> bool:
    """Whether a status code suggests the path exists / is worth reporting."""
    if status in (0, 404, 400, 410):
        return False
    return 200 <= status < 600


def _base_url(domain: str) -> str:
    domain = (domain or "").strip()
    if domain.startswith("http"):
        return domain.rstrip("/")
    return "https://" + domain.strip("/")


def check_path(base_url: str, path: str, timeout: float = 5.0) -> PathEntry | None:
    url = f"{base_url}/{path.lstrip('/')}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):  # type: ignore[override]
            return None  # keep 3xx so we can report them

    opener = urllib.request.build_opener(
        _NoRedirect, urllib.request.HTTPSHandler(context=ctx)
    )
    req = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "Mozilla/5.0 (WebDissect)"}
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.status
            ctype = resp.headers.get("Content-Type", "").split(";")[0]
            length = int(resp.headers.get("Content-Length") or 0)
    except urllib.error.HTTPError as exc:
        status = exc.code
        ctype = exc.headers.get("Content-Type", "").split(";")[0] if exc.headers else ""
        length = 0
    except Exception:
        return None

    if not is_interesting(status):
        return None
    return PathEntry(path="/" + path.lstrip("/"), status=status, content_type=ctype, length=length)


def enumerate_paths(
    domain: str,
    wordlist: list[str] | None = None,
    workers: int = 30,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[PathEntry]:
    base = _base_url(domain)
    words = wordlist or WORDLIST
    results: list[PathEntry] = []
    done = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_path, base, w) for w in words]
        for future in futures:
            entry = future.result()
            done += 1
            if entry is not None:
                results.append(entry)
            if on_progress:
                on_progress(done, len(words))

    results.sort(key=lambda e: e.path)
    return results
