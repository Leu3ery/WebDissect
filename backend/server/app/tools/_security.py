import socket
import ssl
from datetime import datetime

from app.api.schemas.security_check import SecurityCheck
from app.core.logging import get_logger
from app.tools._ssl import fetch_certificate
from app.tools._tech import _fetch

logger = get_logger(__name__)


def _check(category: str, name: str, status: str, severity: str, detail: str) -> SecurityCheck:
    return SecurityCheck(category=category, name=name, status=status, severity=severity, detail=detail)


# --- Security headers (pure) ---------------------------------------------

# header key -> (display name, severity when missing, recommendation)
_REQUIRED_HEADERS = {
    "strict-transport-security": ("Strict-Transport-Security", "medium",
        "Enforce HTTPS with HSTS (e.g. max-age=31536000; includeSubDomains)."),
    "content-security-policy": ("Content-Security-Policy", "high",
        "Define a CSP to mitigate XSS and data injection."),
    "x-content-type-options": ("X-Content-Type-Options", "low",
        "Set 'nosniff' to stop MIME-type sniffing."),
    "x-frame-options": ("X-Frame-Options", "medium",
        "Set DENY/SAMEORIGIN (or CSP frame-ancestors) to prevent clickjacking."),
    "referrer-policy": ("Referrer-Policy", "low",
        "Set a Referrer-Policy to control referrer leakage."),
    "permissions-policy": ("Permissions-Policy", "low",
        "Restrict powerful browser features via Permissions-Policy."),
}


def audit_headers(headers: dict[str, str]) -> list[SecurityCheck]:
    """Audit security headers. ``headers`` keys must be lower-case (pure)."""
    checks: list[SecurityCheck] = []
    csp = headers.get("content-security-policy", "")

    for key, (label, severity, rec) in _REQUIRED_HEADERS.items():
        value = headers.get(key, "")
        # X-Frame-Options is satisfied by CSP frame-ancestors as well.
        if key == "x-frame-options" and "frame-ancestors" in csp.lower():
            checks.append(_check("header", label, "ok", "info", "Covered by CSP frame-ancestors."))
            continue
        if value:
            checks.append(_check("header", label, "ok", "info", value[:200]))
        else:
            checks.append(_check("header", label, "fail", severity, rec))

    # Information disclosure
    for key, label in (("server", "Server"), ("x-powered-by", "X-Powered-By")):
        value = headers.get(key, "")
        if value:
            checks.append(_check(
                "header", f"{label} disclosure", "warn", "low",
                f"Reveals '{value}'. Consider hiding software/version banners.",
            ))

    # Cookie flags (approximate over the combined Set-Cookie value)
    cookies = headers.get("set-cookie", "").lower()
    if cookies:
        flag_names = {"httponly": "HttpOnly", "secure": "Secure", "samesite": "SameSite"}
        missing = [label for flag, label in flag_names.items() if flag not in cookies]
        if missing:
            checks.append(_check(
                "cookie", "Cookie flags", "warn", "medium",
                f"Cookies missing: {', '.join(missing)}.",
            ))
        else:
            checks.append(_check("cookie", "Cookie flags", "ok", "info", "HttpOnly, Secure, SameSite present."))

    return checks


# --- TLS audit (network) --------------------------------------------------

def _negotiated(host: str, port: int = 443, timeout: int = 5) -> tuple[str, str] | None:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                return ssock.version() or "", cipher[0] if cipher else ""
    except (OSError, ssl.SSLError):
        return None


def _legacy_enabled(host: str, version: ssl.TLSVersion, port: int = 443, timeout: int = 4) -> bool | None:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        ctx.minimum_version = version
        ctx.maximum_version = version
    except ValueError:
        return None  # this Python/OpenSSL build can't even speak it
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True
    except (ssl.SSLError, OSError):
        return False


def audit_tls(host: str) -> list[SecurityCheck]:
    checks: list[SecurityCheck] = []

    negotiated = _negotiated(host)
    if negotiated is None:
        checks.append(_check("tls", "TLS handshake", "fail", "high", "Could not establish a TLS connection."))
        return checks

    protocol, cipher = negotiated
    weak = protocol in ("TLSv1", "TLSv1.1", "SSLv3")
    checks.append(_check(
        "tls", "Negotiated protocol", "fail" if weak else "ok",
        "high" if weak else "info", f"{protocol} ({cipher})",
    ))

    for label, version in (("TLS 1.0", ssl.TLSVersion.TLSv1), ("TLS 1.1", ssl.TLSVersion.TLSv1_1)):
        enabled = _legacy_enabled(host, version)
        if enabled:
            checks.append(_check("tls", f"{label} enabled", "fail", "high",
                                 f"Legacy {label} is supported and should be disabled."))
        elif enabled is False:
            checks.append(_check("tls", f"{label} disabled", "ok", "info", f"{label} is not accepted."))

    cert = fetch_certificate(host)
    if cert is not None:
        days = (cert.valid_to - datetime.utcnow()).days
        if days < 0:
            checks.append(_check("tls", "Certificate validity", "fail", "high", "Certificate has expired."))
        elif days < 15:
            checks.append(_check("tls", "Certificate validity", "warn", "medium", f"Expires in {days} days."))
        else:
            checks.append(_check("tls", "Certificate validity", "ok", "info", f"Valid for {days} more days."))

    return checks


def audit(domain: str) -> list[SecurityCheck]:
    """Full security audit: headers + TLS for ``domain``."""
    from app.tools._subdomains import hostname

    host = hostname(domain)
    checks: list[SecurityCheck] = []
    try:
        headers, _body = _fetch(domain)
        checks.extend(audit_headers(headers))
    except Exception as exc:
        logger.info("Header audit failed for %s: %s", domain, exc)
    checks.extend(audit_tls(host))
    return checks
