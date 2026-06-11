import hashlib
import socket
import ssl
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed448, ed25519, rsa
from cryptography.x509.oid import NameOID

from app.api.schemas.certificate import Certificate
from app.core.logging import get_logger

logger = get_logger(__name__)


def _attr(name: x509.Name, oid) -> str | None:
    try:
        attrs = name.get_attributes_for_oid(oid)
        return attrs[0].value if attrs else None
    except Exception:
        return None


def _public_key_type(cert: x509.Certificate) -> str:
    key = cert.public_key()
    if isinstance(key, rsa.RSAPublicKey):
        return "RSA"
    if isinstance(key, ec.EllipticCurvePublicKey):
        return "EC"
    if isinstance(key, dsa.DSAPublicKey):
        return "DSA"
    if isinstance(key, ed25519.Ed25519PublicKey):
        return "Ed25519"
    if isinstance(key, ed448.Ed448PublicKey):
        return "Ed448"
    return "Unknown"


def _not_before(cert: x509.Certificate) -> datetime:
    return getattr(cert, "not_valid_before_utc", None) or cert.not_valid_before


def _not_after(cert: x509.Certificate) -> datetime:
    return getattr(cert, "not_valid_after_utc", None) or cert.not_valid_after


def fetch_certificate(domain: str, port: int = 443, timeout: int = 5) -> Certificate | None:
    """Fetch and parse the TLS certificate served by ``domain`` (SSL/TLS check)."""
    ctx = ssl.create_default_context()
    # Accept self-signed / expired certs so we can still report on them.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                der = ssock.getpeercert(binary_form=True)
    except (socket.gaierror, socket.timeout, ConnectionError, ssl.SSLError, OSError) as exc:
        logger.info("Could not fetch certificate for %s: %s", domain, exc)
        return None

    if not der:
        return None

    cert = x509.load_der_x509_certificate(der)
    subject, issuer = cert.subject, cert.issuer

    return Certificate(
        subject_domain=_attr(subject, NameOID.COMMON_NAME) or domain,
        subject_organization=_attr(subject, NameOID.ORGANIZATION_NAME) or "",
        subject_country=_attr(subject, NameOID.COUNTRY_NAME) or "",
        issuer_name=_attr(issuer, NameOID.COMMON_NAME) or "",
        issuer_organization=_attr(issuer, NameOID.ORGANIZATION_NAME) or "",
        issuer_country=_attr(issuer, NameOID.COUNTRY_NAME) or "",
        valid_from=_not_before(cert).replace(tzinfo=None)
        if _not_before(cert).tzinfo
        else _not_before(cert),
        valid_to=_not_after(cert).replace(tzinfo=None)
        if _not_after(cert).tzinfo
        else _not_after(cert),
        serial_number=format(cert.serial_number, "x"),
        public_key_type=_public_key_type(cert),
        fingerprint_sha256=hashlib.sha256(der).hexdigest(),
    )
