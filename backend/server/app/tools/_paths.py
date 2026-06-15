import random
import ssl
import string
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, NamedTuple

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


class Response(NamedTuple):
    status: int
    content_type: str
    length: int
    sample: str


class Baseline(NamedTuple):
    """Signature of a 'not found' response on servers that don't return 404."""
    status: int
    length: int
    sample: str


def is_interesting(status: int) -> bool:
    """Whether a status code suggests the path exists / is worth reporting."""
    if status in (0, 404, 400, 410):
        return False
    return 200 <= status < 600


def is_soft_404(resp: Response, baseline: Baseline | None) -> bool:
    """Detect a catch-all 'not found' page returned with a non-404 status.

    True when the response closely matches the baseline captured from a known
    non-existent path (same status + near-identical body), so it should NOT be
    reported as a discovered path.
    """
    if baseline is None:
        return False
    if resp.status != baseline.status:
        return False
    if resp.sample and resp.sample == baseline.sample:
        return True
    tolerance = max(64, int(baseline.length * 0.05))
    return abs(resp.length - baseline.length) <= tolerance


def _opener(ctx: ssl.SSLContext) -> urllib.request.OpenerDirector:
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):  # type: ignore[override]
            return None  # keep 3xx so we can report them

    return urllib.request.build_opener(_NoRedirect, urllib.request.HTTPSHandler(context=ctx))


def _request(base_url: str, path: str, timeout: float = 5.0) -> Response | None:
    url = f"{base_url}/{path.lstrip('/')}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (WebDissect)"})
    try:
        with _opener(ctx).open(req, timeout=timeout) as resp:
            body = resp.read(4096)
            return Response(resp.status, resp.headers.get("Content-Type", "").split(";")[0],
                            int(resp.headers.get("Content-Length") or len(body)), body[:512].decode("latin-1", "ignore"))
    except urllib.error.HTTPError as exc:
        ctype = exc.headers.get("Content-Type", "").split(";")[0] if exc.headers else ""
        return Response(exc.code, ctype, 0, "")
    except Exception:
        return None


def _random_path() -> str:
    return "wd-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def probe_baseline(base_url: str) -> Baseline | None:
    """Probe two random non-existent paths; if the server answers with a
    non-404 catch-all, capture its signature for soft-404 filtering."""
    samples = [_request(base_url, _random_path()) for _ in range(2)]
    samples = [s for s in samples if s is not None]
    if not samples:
        return None
    first = samples[0]
    if not is_interesting(first.status):
        return None  # server returns a proper 404 — no soft-404 handling needed
    return Baseline(status=first.status, length=first.length, sample=first.sample)


def check_path(base_url: str, path: str, baseline: Baseline | None = None,
               timeout: float = 5.0) -> PathEntry | None:
    resp = _request(base_url, path, timeout)
    if resp is None or not is_interesting(resp.status) or is_soft_404(resp, baseline):
        return None
    return PathEntry(path="/" + path.lstrip("/"), status=resp.status,
                     content_type=resp.content_type, length=resp.length)


def _base_url(domain: str) -> str:
    domain = (domain or "").strip()
    if domain.startswith("http"):
        return domain.rstrip("/")
    return "https://" + domain.strip("/")


def enumerate_paths(
    domain: str,
    wordlist: list[str] | None = None,
    workers: int = 30,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[PathEntry]:
    base = _base_url(domain)
    words = wordlist or WORDLIST
    baseline = probe_baseline(base)
    if baseline is not None:
        logger.info("Soft-404 baseline for %s: status=%s len=%s", base, baseline.status, baseline.length)

    results: list[PathEntry] = []
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_path, base, w, baseline) for w in words]
        for future in futures:
            entry = future.result()
            done += 1
            if entry is not None:
                results.append(entry)
            if on_progress:
                on_progress(done, len(words))

    results.sort(key=lambda e: e.path)
    return results
