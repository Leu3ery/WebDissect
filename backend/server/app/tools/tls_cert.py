import ssl
import socket
from cryptography import x509
from cryptography.x509 import load_der_x509_certificate, DNSName, ExtensionNotFound
from cryptography.x509.oid import ExtensionOID, NameOID
from cryptography.hazmat.primitives import hashes

from app.db.models import Certificate


def fetch_cert(domain: str, port: int = 443) -> x509.Certificate | None:
    """
    Fetch TLS Certificate for a specific IP address

    Returns:
        Certificate | None: current certificate for the domain, None if no certificate was presented

    Raises:
        socket.gaierror: when DNS resolution fails
        ConnectionRefusedError: when target port is closed
        TimeoutError: when connection timed out
        ValueError: when an invalid port was specified
        OSError: connection reset / unexpected error occurred
        ssl.SSLError: when SSL related error occurred
    """
    if not 0 < port <= 65535:
        raise ValueError("Invalid port specified")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((domain, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
            crt = ssock.getpeercert(binary_form=True)
            if not crt:
                return None
            return load_der_x509_certificate(crt)





def parse_cert(cert: x509.Certificate):
    subject = cert.subject
    issuer = cert.issuer

    def first(name, oid):
        vals = name.get_attributes_for_oid(oid)
        return vals[0].value if vals else None

    # CN is often missing on modern certs — fall back to first SAN
    cn = first(subject, NameOID.COMMON_NAME)
    if cn is None:
        try:
            san = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
            names = san.get_values_for_type(DNSName)
            cn = names[0] if names else None
        except ExtensionNotFound:
            cn = None

    pub = cert.public_key().__class__.__name__  # e.g. 'RSAPublicKey'
    key_type = "RSA" if "RSA" in pub else "EC" if "Elliptic" in pub else pub[:10]

    return Certificate(
        subject_domain       = cn,
        subject_organization = first(subject, NameOID.ORGANIZATION_NAME),
        subject_country      = first(subject, NameOID.COUNTRY_NAME),
        issuer_name          = first(issuer, NameOID.COMMON_NAME),
        issuer_organization  = first(issuer, NameOID.ORGANIZATION_NAME),
        issuer_country       = first(issuer, NameOID.COUNTRY_NAME),
        valid_from           = cert.not_valid_before_utc.replace(tzinfo=None),  # strip tz
        valid_to             = cert.not_valid_after_utc.replace(tzinfo=None),
        serial_number        = format(cert.serial_number, "x"),
        public_key_type      = key_type,
        fingerprint_sha256   = cert.fingerprint(hashes.SHA256()).hex(),
    )