from datetime import datetime, timezone

from fpdf import FPDF

ACCENT = (0, 150, 190)
DARK = (26, 29, 39)
MUTED = (110, 118, 130)
OK = (20, 140, 80)
WARN = (200, 140, 20)
FAIL = (200, 50, 80)

_STATUS_COLOR = {"ok": OK, "warn": WARN, "fail": FAIL, "info": MUTED}


def _safe(value) -> str:
    """Core PDF fonts are latin-1 only — drop anything they can't encode."""
    return str(value).encode("latin-1", "replace").decode("latin-1")


class _Report(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "WebDissect Report", align="L")
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _section(pdf: _Report, title: str) -> None:
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.ln(3)
    pdf.set_fill_color(*DARK)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, f"  {_safe(title)}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_text_color(30, 30, 30)


def _table(pdf: _Report, headings: list[str], rows: list[list[str]], widths: list[float]) -> None:
    if not rows:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 7, "  No data", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(30, 30, 30)
        return
    pdf.set_font("Helvetica", "", 8)
    from fpdf.fonts import FontFace

    with pdf.table(
        col_widths=tuple(widths),
        text_align="LEFT",
        headings_style=FontFace(emphasis="B", color=(255, 255, 255), fill_color=ACCENT),
        line_height=6,
    ) as table:
        table.row(headings)
        for r in rows:
            table.row([_safe(c) for c in r])


def build_pdf(data: dict) -> bytes:
    pdf = _Report()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cover / title
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 38, style="F")
    pdf.set_xy(12, 10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "WebDissect", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Website reconnaissance report")
    pdf.ln(18)

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 9, _safe(data.get("name", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 7, _safe("https://" + data.get("domain", "")), new_x="LMARGIN", new_y="NEXT")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 6, f"Generated {generated}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(30, 30, 30)

    # Summary
    summary = [
        ["DNS records", len(data.get("dns_entries", []))],
        ["Subdomains", len(data.get("subdomains", []))],
        ["Open ports", len(data.get("ports", []))],
        ["Paths", len(data.get("path_entries", []))],
        ["Endpoints", len(data.get("endpoints", []))],
        ["Technologies", len(data.get("technologies", []))],
        ["Security checks", len(data.get("security_checks", []))],
        ["Certificates", len(data.get("certificates", []))],
    ]
    _section(pdf, "Summary")
    _table(pdf, ["Category", "Count"], [[k, str(v)] for k, v in summary], [120, 40])

    # Security findings
    _section(pdf, "Security findings")
    sec_rows = [
        [s.get("severity", ""), s.get("name", ""), s.get("status", ""), s.get("detail", "")]
        for s in data.get("security_checks", [])
    ]
    _table(pdf, ["Severity", "Check", "Status", "Detail"], sec_rows, [22, 45, 20, 93])

    # DNS
    _section(pdf, "DNS records")
    _table(pdf, ["Type", "Name", "Value", "TTL"],
           [[d.get("type", ""), d.get("domain", ""), d.get("value", ""), d.get("ttl", "")]
            for d in data.get("dns_entries", [])], [18, 45, 95, 22])

    # Subdomains
    _section(pdf, "Subdomains")
    _table(pdf, ["Subdomain", "IP", "Source"],
           [[s.get("name", ""), s.get("ip", ""), s.get("source", "")]
            for s in data.get("subdomains", [])], [95, 55, 30])

    # Ports
    _section(pdf, "Open ports")
    _table(pdf, ["Port", "Service", "Version", "Banner"],
           [[f"{p.get('port')}/{p.get('protocol')}", p.get("service", ""), p.get("version", ""), p.get("banner", "")]
            for p in data.get("ports", [])], [22, 32, 42, 84])

    # Paths
    _section(pdf, "Discovered paths")
    _table(pdf, ["Path", "Status", "Content-Type"],
           [[p.get("path", ""), p.get("status", ""), p.get("content_type", "")]
            for p in data.get("path_entries", [])], [110, 25, 45])

    # Endpoints
    _section(pdf, "Endpoints")
    _table(pdf, ["Method", "Path", "Status", "Type"],
           [[e.get("method", ""), e.get("path", ""), e.get("status", ""), e.get("content_type", "")]
            for e in data.get("endpoints", [])], [22, 95, 20, 43])

    # Technologies
    _section(pdf, "Technologies")
    _table(pdf, ["Name", "Description"],
           [[t.get("name", ""), t.get("description", "")] for t in data.get("technologies", [])],
           [50, 130])

    # Certificate
    _section(pdf, "SSL/TLS certificate")
    cert_rows = []
    for c in data.get("certificates", []):
        cert_rows.append(["Subject", c.get("subject_domain", "")])
        cert_rows.append(["Issuer", c.get("issuer_name", "")])
        cert_rows.append(["Valid until", c.get("valid_to", "")])
        cert_rows.append(["Public key", c.get("public_key_type", "")])
        cert_rows.append(["SHA-256", c.get("fingerprint_sha256", "")])
    _table(pdf, ["Field", "Value"], cert_rows, [40, 140])

    output = pdf.output()
    return bytes(output)
