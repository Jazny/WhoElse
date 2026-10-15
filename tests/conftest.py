"""Fixtures shared by the CLI and integration tests."""

import pytest

from fakes import FakeClient
from npc_dm import cli
from npc_dm.chat import NPCChat
from npc_dm.memory import NPCMemory


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the CLI at an empty temporary folder instead of the real npcs/."""
    monkeypatch.setattr(cli, "DATA_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def fake_client(data_dir, monkeypatch):
    """Make the CLI talk to a fake Claude. Tests read fake_client.calls."""
    client = FakeClient()
    monkeypatch.setattr(
        cli, "_make_chat", lambda: NPCChat(NPCMemory(data_dir), client=client)
    )
    return client
