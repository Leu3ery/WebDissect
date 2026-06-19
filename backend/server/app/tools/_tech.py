import re
import ssl
import urllib.request

from app.api.schemas.technology import Technology
from app.core.logging import get_logger

logger = get_logger(__name__)

_ICON = "https://icon.icepanel.io/Technology/svg/{}.svg"


def _tech(name: str, description: str, icon: str) -> Technology:
    return Technology(name=name, description=description, icon_url=_ICON.format(icon))


# name -> (Technology factory). Catalog of things we know how to render nicely.
_CATALOG = {
    "Nginx": lambda: _tech("Nginx", "Web server / reverse proxy", "NGINX"),
    "Apache": lambda: _tech("Apache", "Web server", "Apache"),
    "Cloudflare": lambda: _tech("Cloudflare", "CDN / WAF", "Cloudflare"),
    "PHP": lambda: _tech("PHP", "Server-side language", "PHP"),
    "WordPress": lambda: _tech("WordPress", "CMS", "WordPress"),
    "Node.js": lambda: _tech("Node.js", "JavaScript runtime", "Node.js"),
    "Express": lambda: _tech("Express", "Node.js web framework", "Express"),
    "ASP.NET": lambda: _tech("ASP.NET", "Microsoft web framework", "NET-core"),
    "Django": lambda: _tech("Django", "Python web framework", "Django"),
    "Laravel": lambda: _tech("Laravel", "PHP framework", "Laravel"),
    "React": lambda: _tech("React", "Frontend library", "React"),
    "Vue.js": lambda: _tech("Vue.js", "Frontend framework", "Vue.js"),
    "Angular": lambda: _tech("Angular", "Frontend framework", "Angular"),
    "Next.js": lambda: _tech("Next.js", "React framework", "Next.js"),
    "Java": lambda: _tech("Java", "Server-side platform", "Java"),
    "Ruby on Rails": lambda: _tech("Ruby on Rails", "Ruby web framework", "Rails"),
    "Drupal": lambda: _tech("Drupal", "CMS", "Drupal"),
    "Shopify": lambda: _tech("Shopify", "E-commerce platform", "Shopify"),
    "Vercel": lambda: _tech("Vercel", "Hosting / edge platform", "Vercel"),
}


def _fetch(domain: str, timeout: int = 6) -> tuple[dict[str, str], str]:
    url = domain if domain.startswith("http") else f"https://{domain}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (WebDissect analysis)"}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        # Header keys are case-insensitive; normalise to lower-case.
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.read(200_000).decode("utf-8", errors="ignore")
    return headers, body


def fingerprint(domain: str) -> list[Technology]:
    """Best-effort technology detection from HTTP headers and HTML markers."""
    try:
        headers, body = _fetch(domain)
    except Exception as exc:
        logger.info("Tech fingerprint failed for %s: %s", domain, exc)
        return []

    found: set[str] = set()

    server = headers.get("server", "").lower()
    powered = headers.get("x-powered-by", "").lower()
    cookies = headers.get("set-cookie", "").lower()
    via = headers.get("via", "").lower()
    blob = " ".join([server, powered, via, cookies])
    body_l = body.lower()

    def add(name: str) -> None:
        if name in _CATALOG:
            found.add(name)

    # Header / cookie based
    if "nginx" in server:
        add("Nginx")
    if "apache" in server:
        add("Apache")
    if "cloudflare" in server or "cf-ray" in headers:
        add("Cloudflare")
    if "php" in powered or "phpsessid" in cookies:
        add("PHP")
    if "express" in powered:
        add("Express")
    if "asp.net" in powered or ".aspnet" in cookies or "x-aspnet-version" in headers:
        add("ASP.NET")
    if "vercel" in server or "x-vercel-id" in headers:
        add("Vercel")
    if "jsessionid" in cookies:
        add("Java")
    if "laravel_session" in cookies:
        add("Laravel")
    if "csrftoken" in cookies or "django" in blob:
        add("Django")
    if "x-shopify-stage" in headers or "shopify" in blob:
        add("Shopify")
    if "x-drupal-cache" in headers or "x-generator" in headers and "drupal" in headers.get("x-generator", "").lower():
        add("Drupal")

    # HTML marker based
    if "wp-content" in body_l or "wp-includes" in body_l:
        add("WordPress")
    if "/_next/" in body_l or '"next_data"' in body_l or "__next_data__" in body_l:
        add("Next.js")
    if re.search(r"\breact(dom)?\b", body_l) or "data-reactroot" in body_l:
        add("React")
    if "ng-version" in body_l or "ng-app" in body_l:
        add("Angular")
    if "__vue__" in body_l or "data-v-" in body_l or 'id="app"' in body_l and "vue" in body_l:
        add("Vue.js")
    if "drupal" in body_l:
        add("Drupal")

    generator = headers.get("x-generator", "") + " " + (
        re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', body_l).group(1)
        if re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', body_l)
        else ""
    )
    if "wordpress" in generator.lower():
        add("WordPress")

    return [_CATALOG[name]() for name in sorted(found)]
