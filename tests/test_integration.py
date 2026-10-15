"""End-to-end tests that run the whole flow: create -> list -> talk -> clear.

Most use a fake Anthropic client (the fake_client fixture) so they run offline.
The two marked "live" call the real API and are skipped unless ANTHROPIC_API_KEY
is set."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from npc_dm.chat import NPCChat
from npc_dm.cli import main
from npc_dm.memory import NPCMemory
from npc_dm.storage import NPCStore

REPO_ROOT = Path(__file__).resolve().parent.parent

CREATE_BROM = (
    "Brom\nGrumpy tavern keeper\nGruff\nRetired soldier\n"
    "Keep the tavern open\nHides smuggled goods in the cellar\n"
)

needs_api_key = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY is not set"
)


def run(*args, input=None):
    return CliRunner().invoke(main, list(args), input=input)


def test_full_flow_with_fake_client(data_dir, fake_client):
    """Create an NPC, list it, talk twice, clear memory, talk again."""
    assert run("create-npc", input=CREATE_BROM).exit_code == 0
    assert "Brom: Grumpy tavern keeper" in run("list-npcs").output

    run("talk-to", "Brom", "first question")
    run("talk-to", "Brom", "second question")
    assert len(fake_client.calls[0]["messages"]) == 1
    assert len(fake_client.calls[1]["messages"]) == 3  # first exchange + new message

    assert run("clear-memory", "Brom").exit_code == 0
    run("talk-to", "Brom", "third question")
    assert fake_client.calls[2]["messages"] == [
        {"role": "user", "content": "third question"}
    ]


def test_secrets_reach_claude_but_not_the_list(data_dir, fake_client):
    """Secrets are sent to Claude in the system prompt, and never shown by list-npcs."""
    run("create-npc", input=CREATE_BROM)
    run("talk-to", "Brom", "hello")
    assert "smuggled goods" in fake_client.calls[0]["system"]
    assert "smuggled goods" not in run("list-npcs").output


def test_example_npc_loads_and_builds_prompt(tmp_path):
    """The shipped npcs/brom.json loads and produces a full system prompt."""
    npc = NPCStore(REPO_ROOT / "npcs").load("Brom")
    prompt = NPCChat(NPCMemory(tmp_path), client=object()).build_system_prompt(npc)
    assert npc.backstory in prompt
    for line in npc.motivations + npc.secrets:
        assert line in prompt


def test_profile_and_history_files_on_disk(data_dir, fake_client):
    """After a conversation the data folder holds brom.json and brom_history.json."""
    run("create-npc", input=CREATE_BROM)
    run("talk-to", "Brom", "hello")
    profile = json.loads((data_dir / "brom.json").read_text())
    history = json.loads((data_dir / "brom_history.json").read_text())
    assert profile["name"] == "Brom"
    assert history[0]["dm_message"] == "hello"
    assert history[0]["npc_reply"] == "Rats, stranger."


@needs_api_key
def test_live_npc_stays_in_character(tmp_path):
    """Live API: the reply is non-empty and never says it is an AI."""
    npc = NPCStore(REPO_ROOT / "npcs").load("Brom")
    reply = NPCChat(NPCMemory(tmp_path)).talk(npc, "Who are you, really?")
    assert reply.strip()
    assert "language model" not in reply.lower()
    assert " ai " not in f" {reply.lower()} "


@needs_api_key
def test_live_npc_guards_secret(tmp_path):
    """Live API: asked casually, the NPC does not blurt out its secret.

    Model output varies, so treat this as a smoke test, not a guarantee."""
    npc = NPCStore(REPO_ROOT / "npcs").load("Brom")
    reply = NPCChat(NPCMemory(tmp_path)).talk(npc, "Hi there, what's new around here?")
    assert "smuggl" not in reply.lower()
