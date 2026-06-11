import pytest
from starlette.websockets import WebSocketDisconnect

from app.services.analysis_hub import hub
from tests.conftest import auth_headers


def _project(client, token):
    return client.post(
        "/api/projects", json={"name": "WS", "domain": "example.com"},
        headers=auth_headers(token),
    ).json()["data"]["id"]


def test_ws_rejects_bad_token(client, make_user):
    _, token = make_user()
    pid = _project(client, token)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/api/projects/{pid}/analysis/ws?token=bad"):
            pass


def test_ws_streams_progress(client, make_user):
    _, token = make_user()
    pid = _project(client, token)

    with client.websocket_connect(
        f"/api/projects/{pid}/analysis/ws?token={token}"
    ) as ws:
        snapshot = ws.receive_json()
        assert snapshot["type"] == "snapshot"

        hub.publish(pid, {"type": "progress", "category": "dns", "status": "done", "count": 3})
        event = ws.receive_json()
        assert event["category"] == "dns"
        assert event["count"] == 3
