"""Tests for npc_dm/web.py. Each test starts the real server on a free port in a
background thread and talks to it over HTTP, with a fake Claude and a temporary
data folder."""

import json
import threading
import urllib.error
import urllib.request

import anthropic
import pytest

from fakes import FakeClient
from npc_dm.chat import NPCChat
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC
from npc_dm.storage import NPCStore
from npc_dm.web import WebApp, WebError, make_server


@pytest.fixture
def client():
    return FakeClient()


@pytest.fixture
def base_url(tmp_path, client):
    app = WebApp(tmp_path, make_chat=lambda: NPCChat(NPCMemory(tmp_path), client=client))
    server = make_server(app, port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def request(base_url, method, path, body=None):
    """Return (status, parsed JSON or text)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base_url + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as response:
            status, raw, kind = response.status, response.read(), response.headers["Content-Type"]
    except urllib.error.HTTPError as error:
        status, raw, kind = error.code, error.read(), error.headers["Content-Type"]
    return status, json.loads(raw) if kind == "application/json" else raw.decode()


def save_brom(tmp_path):
    NPCStore(tmp_path).save(
        NPC(
            name="Brom",
            personality="Grumpy tavern keeper.",
            voice="Gruff.",
            secrets=["Hides smuggled goods in the cellar"],
        )
    )


def test_page_is_served(base_url):
    status, page = request(base_url, "GET", "/")
    assert status == 200
    assert "<title>WhoElse</title>" in page


def test_list_hides_secrets(base_url, tmp_path):
    save_brom(tmp_path)
    status, npcs = request(base_url, "GET", "/api/npcs")
    assert status == 200
    assert npcs == [{"name": "Brom", "personality": "Grumpy tavern keeper."}]


def test_profile_shows_everything_entered(base_url, tmp_path):
    """The character information box gets the full profile, secrets included."""
    save_brom(tmp_path)
    status, npc = request(base_url, "GET", "/api/npcs/brom")
    assert status == 200
    assert npc["name"] == "Brom"
    assert npc["voice"] == "Gruff."
    assert npc["secrets"] == ["Hides smuggled goods in the cellar"]


def test_profile_unknown_npc_is_404(base_url):
    status, data = request(base_url, "GET", "/api/npcs/Nobody")
    assert status == 404
    assert "No NPC named 'Nobody'" in data["error"]


def test_create_npc_saves_profile(base_url, tmp_path):
    body = {
        "name": "Mira",
        "personality": "Curious apprentice",
        "voice": "Bright",
        "motivations": "Learn magic; Find her brother ;;",
        "secrets": "",
    }
    status, _ = request(base_url, "POST", "/api/npcs", body)
    assert status == 200
    npc = NPCStore(tmp_path).load("Mira")
    assert npc.motivations == ["Learn magic", "Find her brother"]
    assert npc.secrets == []


def test_create_npc_needs_required_fields(base_url):
    status, data = request(base_url, "POST", "/api/npcs", {"name": "Mira"})
    assert status == 400
    assert "personality" in data["error"]


def test_create_npc_existing_name_is_refused(base_url, tmp_path):
    save_brom(tmp_path)
    body = {"name": "brom", "personality": "x", "voice": "y"}
    status, data = request(base_url, "POST", "/api/npcs", body)
    assert status == 409
    assert "already exists" in data["error"]


def test_send_message_replies_and_remembers(base_url, tmp_path, client):
    save_brom(tmp_path)
    status, data = request(base_url, "POST", "/api/npcs/Brom/messages", {"message": "Hi"})
    assert (status, data) == (200, {"reply": "Rats, stranger."})
    request(base_url, "POST", "/api/npcs/brom/messages", {"message": "Sure?"})
    assert client.calls[1]["messages"][0] == {"role": "user", "content": "Hi"}

    status, history = request(base_url, "GET", "/api/npcs/Brom/history")
    assert [item["dm_message"] for item in history] == ["Hi", "Sure?"]


def test_send_blank_message_is_refused(base_url, tmp_path, client):
    save_brom(tmp_path)
    status, _ = request(base_url, "POST", "/api/npcs/Brom/messages", {"message": "  "})
    assert status == 400
    assert client.calls == []


def test_send_api_error_is_reported_and_not_saved(tmp_path):
    client = FakeClient(error=anthropic.AnthropicError("could not reach Claude"))
    app = WebApp(tmp_path, make_chat=lambda: NPCChat(NPCMemory(tmp_path), client=client))
    save_brom(tmp_path)
    with pytest.raises(WebError, match="could not reach Claude"):
        app.send("Brom", "hello")
    assert NPCMemory(tmp_path).get_recent("Brom") == []


def test_unknown_npc_is_404(base_url):
    status, data = request(base_url, "POST", "/api/npcs/Nobody/messages", {"message": "hi"})
    assert status == 404
    assert "No NPC named 'Nobody'" in data["error"]


def test_clear_memory_keeps_profile(base_url, tmp_path):
    save_brom(tmp_path)
    request(base_url, "POST", "/api/npcs/Brom/messages", {"message": "Hi"})
    status, _ = request(base_url, "DELETE", "/api/npcs/Brom/history")
    assert status == 200
    assert NPCMemory(tmp_path).get_recent("Brom") == []
    assert NPCStore(tmp_path).exists("Brom")


def test_names_with_spaces_work(base_url, tmp_path):
    NPCStore(tmp_path).save(NPC(name="Old Brom", personality="p", voice="v"))
    status, _ = request(base_url, "POST", "/api/npcs/Old%20Brom/messages", {"message": "Hi"})
    assert status == 200
