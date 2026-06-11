import re
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.api.schemas.port import Port
from app.core.logging import get_logger

logger = get_logger(__name__)

# A focused "top ports" list for a quick service sweep.
COMMON_PORTS: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    465: "smtps",
    587: "smtp",
    993: "imaps",
    995: "pop3s",
    1433: "mssql",
    2049: "nfs",
    3000: "http",
    3306: "mysql",
    3389: "rdp",
    5432: "postgresql",
    5672: "amqp",
    6379: "redis",
    8000: "http",
    8080: "http-proxy",
    8443: "https-alt",
    9200: "elasticsearch",
    11211: "memcached",
    27017: "mongodb",
}

_HTTP_PORTS = {80, 3000, 8000, 8080}
_TLS_PORTS = {443, 8443, 993, 995, 465}


def guess_service_version(port: int, banner: str) -> tuple[str, str]:
    """Map a port + banner to (service, version) — pure, nmap -sV-lite."""
    service = COMMON_PORTS.get(port, "")
    version = ""
    b = banner.strip()

    if not b:
        return service, ""

    # SSH:  SSH-2.0-OpenSSH_8.9p1 Ubuntu
    m = re.search(r"SSH-[\d.]+-(\S+)", b)
    if m:
        return "ssh", m.group(1).replace("_", " ")

    # HTTP Server header
    m = re.search(r"^server:\s*(.+)$", b, re.IGNORECASE | re.MULTILINE)
    if m:
        return service or "http", m.group(1).strip()

    # FTP / SMTP / POP3 greeting lines often carry the product name
    m = re.search(r"^220[- ](.+)$", b, re.MULTILINE)
    if m:
        return service or "ftp", m.group(1).strip()[:100]

    # Redis / others: first non-empty line
    first = next((ln.strip() for ln in b.splitlines() if ln.strip()), "")
    return service, first[:100]


def _grab_banner(sock: socket.socket, port: int, host: str) -> str:
    sock.settimeout(2.5)
    try:
        if port in _HTTP_PORTS or port in _TLS_PORTS:
            stream: socket.socket = sock
            if port in _TLS_PORTS:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                stream = ctx.wrap_socket(sock, server_hostname=host)
            request = f"HEAD / HTTP/1.0\r\nHost: {host}\r\nUser-Agent: WebDissect\r\n\r\n"
            stream.sendall(request.encode())
            return stream.recv(1024).decode("latin-1", errors="ignore")
        # Generic services often send a greeting on connect.
        return sock.recv(256).decode("latin-1", errors="ignore")
    except (socket.timeout, ssl.SSLError, OSError):
        return ""


def scan_port(host: str, port: int, timeout: float = 1.5) -> Port | None:
    """Return a :class:`Port` if the TCP port is open, else ``None``."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            banner = _grab_banner(sock, port, host)
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None

    service, version = guess_service_version(port, banner)
    snippet = " ".join(banner.split())[:200]
    return Port(
        port=port,
        protocol="tcp",
        state="open",
        service=service,
        version=version,
        banner=snippet,
    )


def scan_ports(
    domain: str,
    ports: list[int] | None = None,
    workers: int = 40,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[Port]:
    host = _hostname(domain)
    target_ports = ports or list(COMMON_PORTS.keys())
    open_ports: list[Port] = []
    done = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(scan_port, host, p): p for p in target_ports}
        for future in futures:
            result = future.result()
            done += 1
            if result is not None:
                open_ports.append(result)
            if on_progress:
                on_progress(done, len(target_ports))

    open_ports.sort(key=lambda p: p.port)
    return open_ports


def _hostname(domain: str) -> str:
    domain = (domain or "").strip()
    if "://" in domain:
        from urllib.parse import urlparse

        domain = urlparse(domain).netloc or domain
    return domain.strip("/").split("/")[0]
