import re
import ssl
import urllib.request

from app.api.schemas.technology import Technology
from app.core.logging import get_logger

logger = get_logger(__name__)

_ICON = "https://icon.icepanel.io/Technology/svg/{}.svg"


def _tech(name: str, description: str, icon: str, version: str = "") -> Technology:
    desc = f"{description} · v{version}" if version else description
    return Technology(name=name, description=desc, icon_url=_ICON.format(icon))


def _version(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1) if m else ""


def detect(headers: dict[str, str], body: str) -> list[Technology]:
    """Pure technology detection from HTTP headers and HTML body.

    ``headers`` keys are expected to be lower-case. No network access — this is
    the unit-testable core of :func:`fingerprint`.
    """
    server = headers.get("server", "")
    powered = headers.get("x-powered-by", "")
    cookies = headers.get("set-cookie", "")
    via = headers.get("via", "")
    generator = headers.get("x-generator", "")
    blob = " ".join([server, powered, via, generator]).lower()
    cookies_l = cookies.lower()
    body_l = body.lower()

    found: dict[str, Technology] = {}

    def add(tech: Technology) -> None:
        found.setdefault(tech.name, tech)

    # --- Web servers / proxies / CDNs (with versions) --------------------
    if "nginx" in server.lower():
        add(_tech("Nginx", "Web server / reverse proxy", "NGINX", _version(r"nginx/([\d.]+)", server)))
    if "apache" in server.lower():
        add(_tech("Apache", "Web server", "Apache", _version(r"apache/([\d.]+)", server)))
    if "cloudflare" in server.lower() or "cf-ray" in headers:
        add(_tech("Cloudflare", "CDN / WAF", "Cloudflare"))
    if "vercel" in server.lower() or "x-vercel-id" in headers:
        add(_tech("Vercel", "Hosting / edge platform", "Vercel"))
    if "litespeed" in server.lower():
        add(_tech("LiteSpeed", "Web server", "LiteSpeed"))
    if "caddy" in server.lower():
        add(_tech("Caddy", "Web server", "Caddy"))
    if "openresty" in server.lower():
        add(_tech("OpenResty", "Nginx-based web platform", "NGINX", _version(r"openresty/([\d.]+)", server)))
    if "amazons3" in server.lower() or "x-amz-request-id" in headers:
        add(_tech("Amazon S3", "Object storage", "Amazon-S3"))
    if "akamai" in blob or "x-akamai-transformed" in headers:
        add(_tech("Akamai", "CDN", "Akamai"))
    if "fastly" in blob or "x-served-by" in headers and "cache" in headers.get("x-served-by", "").lower():
        add(_tech("Fastly", "CDN", "Fastly"))

    # --- Languages / runtimes -------------------------------------------
    if "php" in powered.lower() or "phpsessid" in cookies_l:
        add(_tech("PHP", "Server-side language", "PHP", _version(r"php/([\d.]+)", powered)))
    if "asp.net" in powered.lower() or ".aspnet" in cookies_l or "x-aspnet-version" in headers:
        add(_tech("ASP.NET", "Microsoft web framework", "NET-core", _version(r"([\d.]+)", headers.get("x-aspnet-version", ""))))
    if "express" in powered.lower():
        add(_tech("Express", "Node.js web framework", "Express"))
    if "jsessionid" in cookies_l:
        add(_tech("Java", "Server-side platform", "Java"))

    # --- Frameworks / CMS ------------------------------------------------
    if "wp-content" in body_l or "wp-includes" in body_l or "wordpress" in generator.lower():
        add(_tech("WordPress", "CMS", "WordPress", _version(r"wordpress[ /]([\d.]+)", generator)))
    if "laravel_session" in cookies_l:
        add(_tech("Laravel", "PHP framework", "Laravel"))
    if "csrftoken" in cookies_l or "django" in blob:
        add(_tech("Django", "Python web framework", "Django"))
    if "x-drupal-cache" in headers or "drupal" in body_l or "drupal" in generator.lower():
        add(_tech("Drupal", "CMS", "Drupal"))
    if "x-shopify-stage" in headers or "shopify" in blob:
        add(_tech("Shopify", "E-commerce platform", "Shopify"))
    if "x-magento" in " ".join(headers.keys()) or "magento" in body_l:
        add(_tech("Magento", "E-commerce platform", "Magento"))
    if "rails" in blob or "_rails" in cookies_l:
        add(_tech("Ruby on Rails", "Ruby web framework", "Rails"))

    # --- Frontend libraries (HTML markers) -------------------------------
    if "/_next/" in body_l or "__next_data__" in body_l:
        add(_tech("Next.js", "React framework", "Next.js"))
    if "data-reactroot" in body_l or re.search(r"\breact(dom)?\b", body_l):
        add(_tech("React", "Frontend library", "React"))
    if "ng-version" in body_l or "ng-app" in body_l:
        add(_tech("Angular", "Frontend framework", "Angular", _version(r'ng-version="([\d.]+)"', body)))
    if "__vue__" in body_l or "data-v-" in body_l or "nuxt" in body_l:
        add(_tech("Vue.js", "Frontend framework", "Vue.js"))
    if "__svelte" in body_l or "svelte-" in body_l:
        add(_tech("Svelte", "Frontend framework", "Svelte"))
    if "gatsby" in body_l or "___gatsby" in body_l:
        add(_tech("Gatsby", "React framework", "Gatsby"))

    return list(found.values())


def _fetch(domain: str, timeout: int = 6) -> tuple[dict[str, str], str]:
    url = domain if domain.startswith("http") else f"https://{domain}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (WebDissect analysis)"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.read(200_000).decode("utf-8", errors="ignore")
    return headers, body


def fingerprint(domain: str) -> list[Technology]:
    """Best-effort technology detection by fetching the site, then :func:`detect`."""
    try:
        headers, body = _fetch(domain)
    except Exception as exc:
        logger.info("Tech fingerprint failed for %s: %s", domain, exc)
        return []
    return detect(headers, body)
