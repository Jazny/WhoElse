"""A small local web page for creating NPCs and chatting with them.

Uses only Python's built-in http.server, so there is nothing extra to install.
The page (static/index.html) talks to these JSON endpoints:

    GET    /api/npcs                  list NPCs (name and personality only)
    POST   /api/npcs                  create an NPC
    GET    /api/npcs/<name>           the NPC's full profile, secrets included (DM only)
    GET    /api/npcs/<name>/history   past exchanges, oldest first
    POST   /api/npcs/<name>/messages  send {"message": ...}, get {"reply": ...}
    DELETE /api/npcs/<name>/history   clear the NPC's memory

The chat logic is the same NPCChat the command line uses.
"""

import json
import sys
import threading
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import unquote

import anthropic

from npc_dm.chat import NPCChat
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC
from npc_dm.storage import NPCStore


class WebError(Exception):
    """An error to show on the page, with the HTTP status to send."""

    def __init__(self, status: HTTPStatus, message: str):
        super().__init__(message)
        self.status = status


class WebApp:
    """The actions behind each endpoint, kept apart from HTTP so tests can call them."""

    def __init__(self, data_dir: Path, make_chat: Callable[[], NPCChat] | None = None):
        self.store = NPCStore(data_dir)
        self.memory = NPCMemory(data_dir)
        self._make_chat = make_chat or (lambda: NPCChat(self.memory))
        self._chat: NPCChat | None = None
        # The server answers requests in threads; one turn at a time keeps history files intact.
        self._lock = threading.Lock()

    def list_npcs(self) -> list[dict]:
        # Secrets are left out on purpose, same as list-npcs.
        return [
            {"name": npc.name, "personality": npc.personality}
            for npc in self.store.list_all()
        ]

    def create_npc(self, data: dict) -> dict:
        def text(key: str) -> str:
            return str(data.get(key) or "").strip()

        def items(key: str) -> list[str]:
            value = data.get(key) or []
            if isinstance(value, str):
                value = value.split(";")
            return [str(item).strip() for item in value if str(item).strip()]

        npc = NPC(
            name=text("name"),
            personality=text("personality"),
            voice=text("voice"),
            backstory=text("backstory"),
            motivations=items("motivations"),
            secrets=items("secrets"),
        )
        missing = [key for key in ("name", "personality", "voice") if not getattr(npc, key)]
        if missing:
            raise WebError(HTTPStatus.BAD_REQUEST, f"Please fill in: {', '.join(missing)}.")
        try:
            self.store.save(npc)
        except ValueError as error:
            raise WebError(HTTPStatus.BAD_REQUEST, str(error)) from None
        except FileExistsError:
            raise WebError(
                HTTPStatus.CONFLICT,
                f"An NPC named {npc.name!r} already exists. Overwriting is not supported.",
            ) from None
        return {"name": npc.name, "personality": npc.personality}

    def profile(self, name: str) -> dict:
        # Everything the DM entered, secrets included. The page only shows it on request.
        return self._load(name).to_dict()

    def history(self, name: str) -> list[dict]:
        npc = self._load(name)
        return [exchange.to_dict() for exchange in self.memory.get_recent(npc.name, limit=sys.maxsize)]

    def send(self, name: str, message: str) -> dict:
        npc = self._load(name)
        message = (message or "").strip()
        if not message:
            raise WebError(HTTPStatus.BAD_REQUEST, "Type a message first.")
        try:
            with self._lock:
                if self._chat is None:
                    self._chat = self._make_chat()
                reply = self._chat.talk(npc, message)
        except (RuntimeError, anthropic.AnthropicError) as error:
            raise WebError(HTTPStatus.BAD_GATEWAY, str(error)) from None
        return {"reply": reply}

    def clear(self, name: str) -> dict:
        npc = self._load(name)
        self.memory.clear(npc.name)
        return {"cleared": npc.name}

    def _load(self, name: str) -> NPC:
        try:
            return self.store.load(name)
        except (FileNotFoundError, ValueError):
            raise WebError(HTTPStatus.NOT_FOUND, f"No NPC named {name!r}.") from None


def make_handler(app: WebApp) -> type[BaseHTTPRequestHandler]:
    """Build a request handler class bound to one WebApp."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                page = files("npc_dm").joinpath("static/index.html").read_bytes()
                self._send(HTTPStatus.OK, page, "text/html; charset=utf-8")
            else:
                self._route("GET")

        def do_POST(self):
            self._route("POST")

        def do_DELETE(self):
            self._route("DELETE")

        def _route(self, method: str):
            parts = [unquote(part) for part in self.path.split("?")[0].strip("/").split("/")]
            try:
                if parts[:2] != ["api", "npcs"]:
                    raise WebError(HTTPStatus.NOT_FOUND, "Not found.")
                rest = parts[2:]
                if method == "GET" and not rest:
                    result = app.list_npcs()
                elif method == "POST" and not rest:
                    result = app.create_npc(self._read_json())
                elif len(rest) == 1 and method == "GET":
                    result = app.profile(rest[0])
                elif len(rest) == 2 and rest[1] == "history" and method == "GET":
                    result = app.history(rest[0])
                elif len(rest) == 2 and rest[1] == "history" and method == "DELETE":
                    result = app.clear(rest[0])
                elif len(rest) == 2 and rest[1] == "messages" and method == "POST":
                    result = app.send(rest[0], self._read_json().get("message", ""))
                else:
                    raise WebError(HTTPStatus.NOT_FOUND, "Not found.")
            except WebError as error:
                self._send_json(error.status, {"error": str(error)})
                return
            self._send_json(HTTPStatus.OK, result)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            try:
                data = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                raise WebError(HTTPStatus.BAD_REQUEST, "Request body is not valid JSON.") from None
            if not isinstance(data, dict):
                raise WebError(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object.")
            return data

        def _send_json(self, status: HTTPStatus, data):
            self._send(status, json.dumps(data).encode("utf-8"), "application/json")

        def _send(self, status: HTTPStatus, body: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass  # keep the terminal quiet

    return Handler


def make_server(
    app: WebApp, host: str = "127.0.0.1", port: int = 8000
) -> ThreadingHTTPServer:
    """Create (but do not start) the web server. Port 0 picks a free port."""
    return ThreadingHTTPServer((host, port), make_handler(app))
