from app.tools._tech import detect
from app.tools._subdomains import parse_crtsh, hostname
from app.tools._ports import guess_service_version, COMMON_PORTS
from app.tools._paths import is_interesting
from app.tools._har import parse_har


# --- tech fingerprint -----------------------------------------------------

def test_detect_nginx_php_with_versions():
    headers = {"server": "nginx/1.25.3", "x-powered-by": "PHP/8.2.1"}
    techs = {t.name: t for t in detect(headers, "")}
    assert "Nginx" in techs and "1.25.3" in techs["Nginx"].description
    assert "PHP" in techs and "8.2.1" in techs["PHP"].description


def test_detect_frontend_and_cms_from_body():
    headers = {"server": "cloudflare"}
    body = '<html ng-version="17.1.0"><div class="wp-content">x</div></html>'
    names = {t.name for t in detect(headers, body)}
    assert {"Cloudflare", "Angular", "WordPress"} <= names


def test_detect_empty():
    assert detect({}, "") == []


# --- subdomains -----------------------------------------------------------

def test_parse_crtsh_filters_and_dedups():
    payload = (
        '[{"name_value": "*.example.com\\nwww.example.com"},'
        ' {"name_value": "api.example.com", "common_name": "example.com"},'
        ' {"name_value": "evil.notexample.com"}]'
    )
    names = parse_crtsh(payload, "example.com")
    assert names == ["api.example.com", "example.com", "www.example.com"]


def test_parse_crtsh_invalid_json():
    assert parse_crtsh("not json", "example.com") == []


def test_hostname_strips_scheme_and_path():
    assert hostname("https://Example.com/login") == "example.com"


# --- ports ----------------------------------------------------------------

def test_guess_service_version_ssh():
    service, version = guess_service_version(22, "SSH-2.0-OpenSSH_8.9p1 Ubuntu")
    assert service == "ssh"
    assert "OpenSSH 8.9p1" in version


def test_guess_service_version_http_server_header():
    banner = "HTTP/1.1 200 OK\r\nServer: nginx/1.25.3\r\n\r\n"
    service, version = guess_service_version(80, banner)
    assert service == "http"
    assert version == "nginx/1.25.3"


def test_guess_service_version_defaults_to_port_map():
    service, version = guess_service_version(3306, "")
    assert service == COMMON_PORTS[3306]
    assert version == ""


# --- paths ----------------------------------------------------------------

def test_is_interesting():
    assert is_interesting(200)
    assert is_interesting(301)
    assert is_interesting(403)
    assert not is_interesting(404)
    assert not is_interesting(0)


# --- HAR ------------------------------------------------------------------

def test_parse_har_dedups_and_filters():
    har = """
    {"log": {"entries": [
      {"request": {"method": "GET", "url": "https://x.com/"},
       "response": {"status": 200, "content": {"mimeType": "text/html"}}},
      {"request": {"method": "GET", "url": "https://x.com/"},
       "response": {"status": 200, "content": {"mimeType": "text/html"}}},
      {"request": {"method": "POST", "url": "https://x.com/api?a=1"},
       "response": {"status": 401, "content": {"mimeType": "application/json"}}},
      {"request": {"method": "GET", "url": "https://x.com/fail"},
       "response": {"status": 0, "content": {}}}
    ]}}
    """
    eps = parse_har(har)
    assert len(eps) == 2
    paths = {(e.method, e.path) for e in eps}
    assert ("GET", "/") in paths
    assert ("POST", "/api?a=1") in paths


def test_parse_har_invalid():
    assert parse_har("{nope") == []
