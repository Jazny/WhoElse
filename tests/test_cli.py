"""Tests for npc_dm/cli.py. Uses click.testing.CliRunner, which runs the commands
inside the test and lets us type answers and read the output. The data_dir and
fake_client fixtures (tests/conftest.py) keep every test on a temporary folder
and a fake Claude, so nothing touches real NPCs or the real API."""

import os

import anthropic
from click.testing import CliRunner

from fakes import FakeClient
from npc_dm.cli import main
from npc_dm.chat import NPCChat
from npc_dm.memory import NPCMemory
from npc_dm.models import Exchange, NPC
from npc_dm.storage import NPCStore


def run(*args, input=None):
    return CliRunner().invoke(main, list(args), input=input)


def save_npc(data_dir, name="Brom", **overrides) -> NPC:
    fields = dict(
        name=name,
        personality="Grumpy tavern keeper.",
        voice="Gruff.",
        backstory="Retired soldier.",
        motivations=["Keep the tavern open"],
        secrets=["Hides smuggled goods in the cellar"],
    )
    fields.update(overrides)
    npc = NPC(**fields)
    NPCStore(data_dir).save(npc)
    return npc


# --- create-npc (Feature 1) ---------------------------------------------------


def test_create_npc_saves_profile(data_dir):
    """Answering the prompts saves an NPC that NPCStore can load."""
    answers = "Brom\nGrumpy tavern keeper\nGruff\nRetired soldier\nKeep the tavern open\nHides crates\n"
    result = run("create-npc", input=answers)
    assert result.exit_code == 0
    assert "Saved Brom" in result.output
    assert NPCStore(data_dir).load("Brom") == NPC(
        name="Brom",
        personality="Grumpy tavern keeper",
        voice="Gruff",
        backstory="Retired soldier",
        motivations=["Keep the tavern open"],
        secrets=["Hides crates"],
    )


def test_create_npc_optional_fields_can_be_blank(data_dir):
    """Backstory, motivations and secrets can be skipped with Enter."""
    result = run("create-npc", input="Brom\nGrumpy\nGruff\n\n\n\n")
    assert result.exit_code == 0
    npc = NPCStore(data_dir).load("Brom")
    assert (npc.backstory, npc.motivations, npc.secrets) == ("", [], [])


def test_create_npc_splits_multiple_motivations_and_secrets(data_dir):
    """Several motivations or secrets can be entered, separated by ';'."""
    answers = "Brom\nGrumpy\nGruff\n\nProtect Mira;  Pay the debt ;;\nSecret one; secret two\n"
    run("create-npc", input=answers)
    npc = NPCStore(data_dir).load("Brom")
    assert npc.motivations == ["Protect Mira", "Pay the debt"]
    assert npc.secrets == ["Secret one", "secret two"]


def test_create_npc_existing_name_is_refused(data_dir):
    """Creating an NPC whose name already exists fails and keeps the original."""
    original = save_npc(data_dir)
    for typed_name in ("Brom", "brom"):
        result = run("create-npc", input=f"{typed_name}\n")
        assert result.exit_code != 0
        assert "already exists" in result.output
        assert "Personality" not in result.output  # stopped before the other prompts
        assert "Traceback" not in result.output
    assert NPCStore(data_dir).load("Brom") == original


def test_create_npc_name_without_letters_is_refused(data_dir):
    """A name like "!!!" cannot become a file name, so it gets a clear error."""
    result = run("create-npc", input="!!!\n")
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert NPCStore(data_dir).list_all() == []


# --- list-npcs (Feature 4) ----------------------------------------------------


def test_list_npcs_shows_all(data_dir):
    """Every saved NPC is listed with its name and personality."""
    save_npc(data_dir, "Brom", personality="Grumpy tavern keeper.")
    save_npc(data_dir, "Mira", personality="Curious apprentice.")
    result = run("list-npcs")
    assert result.exit_code == 0
    assert "Brom: Grumpy tavern keeper." in result.output
    assert "Mira: Curious apprentice." in result.output


def test_list_npcs_does_not_reveal_secrets(data_dir):
    """The list is safe to show at the table: secrets never appear."""
    save_npc(data_dir, secrets=["Hides smuggled goods in the cellar"])
    result = run("list-npcs")
    assert "smuggled" not in result.output


def test_list_npcs_empty(data_dir):
    """With no NPCs, a friendly message suggests create-npc."""
    result = run("list-npcs")
    assert result.exit_code == 0
    assert "create-npc" in result.output


# --- talk-to (Feature 2) ------------------------------------------------------


def test_talk_to_prints_reply(data_dir, fake_client):
    """talk-to prints the NPC's reply."""
    save_npc(data_dir)
    result = run("talk-to", "Brom", "What's in the cellar?")
    assert result.exit_code == 0
    assert "Rats, stranger." in result.output


def test_talk_to_name_is_case_insensitive(data_dir, fake_client):
    """"brom" and "Brom" find the same NPC."""
    save_npc(data_dir)
    result = run("talk-to", "brom", "hello")
    assert result.exit_code == 0
    assert "Rats, stranger." in result.output


def test_talk_to_unknown_npc(data_dir, fake_client):
    """Talking to an NPC that does not exist gives a clear error."""
    result = run("talk-to", "Nobody", "hi")
    assert result.exit_code != 0
    assert "No NPC named 'Nobody'" in result.output
    assert "list-npcs" in result.output
    assert "Traceback" not in result.output
    assert fake_client.calls == []


def test_talk_to_remembers_previous_turns(data_dir, fake_client):
    """A second talk-to sends the first exchange back to Claude."""
    save_npc(data_dir)
    run("talk-to", "Brom", "What's in the cellar?")
    run("talk-to", "Brom", "Are you sure?")
    assert fake_client.calls[1]["messages"] == [
        {"role": "user", "content": "What's in the cellar?"},
        {"role": "assistant", "content": "Rats, stranger."},
        {"role": "user", "content": "Are you sure?"},
    ]


def test_talk_to_missing_api_key(data_dir, monkeypatch):
    """Without ANTHROPIC_API_KEY the user is told what to do, with no traceback."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    save_npc(data_dir)
    result = run("talk-to", "Brom", "hello")
    assert result.exit_code != 0
    assert "ANTHROPIC_API_KEY" in result.output
    assert "Traceback" not in result.output


def test_talk_to_api_error_is_readable_and_not_saved(data_dir, monkeypatch):
    """If Claude cannot be reached, the user sees an error and nothing is remembered."""
    client = FakeClient(error=anthropic.AnthropicError("could not reach Claude"))
    monkeypatch.setattr(
        "npc_dm.cli._make_chat", lambda: NPCChat(NPCMemory(data_dir), client=client)
    )
    save_npc(data_dir)
    result = run("talk-to", "Brom", "hello")
    assert result.exit_code != 0
    assert "could not reach Claude" in result.output
    assert "Traceback" not in result.output
    assert NPCMemory(data_dir).get_recent("Brom") == []


# --- chat (Feature 2, conversation mode) -------------------------------------


def test_chat_talks_until_quit(data_dir, fake_client):
    """Each line is sent to the NPC until the DM types quit."""
    save_npc(data_dir)
    result = run("chat", "Brom", input="What's in the cellar?\nAre you sure?\nquit\n")
    assert result.exit_code == 0
    assert result.output.count("Brom: Rats, stranger.") == 2
    assert "Goodbye from Brom" in result.output
    assert len(fake_client.calls) == 2


def test_chat_remembers_earlier_lines(data_dir, fake_client):
    """Later lines in the same conversation include the earlier exchange."""
    save_npc(data_dir)
    run("chat", "Brom", input="first line\nsecond line\nquit\n")
    assert fake_client.calls[1]["messages"] == [
        {"role": "user", "content": "first line"},
        {"role": "assistant", "content": "Rats, stranger."},
        {"role": "user", "content": "second line"},
    ]


def test_chat_quit_is_case_insensitive_and_skips_blank_lines(data_dir, fake_client):
    """"  QUIT  " ends the chat, and empty lines are ignored without calling Claude."""
    save_npc(data_dir)
    result = run("chat", "Brom", input="\n   \n  QUIT  \n")
    assert result.exit_code == 0
    assert fake_client.calls == []


def test_chat_survives_a_failed_turn(data_dir, monkeypatch):
    """If one turn fails, the error is shown and the chat keeps going."""
    client = FakeClient(error=anthropic.AnthropicError("could not reach Claude"))
    monkeypatch.setattr(
        "npc_dm.cli._make_chat", lambda: NPCChat(NPCMemory(data_dir), client=client)
    )
    save_npc(data_dir)
    result = run("chat", "Brom", input="hello\nquit\n")
    assert result.exit_code == 0
    assert "could not reach Claude" in result.output
    assert len(client.calls) == 1
    assert NPCMemory(data_dir).get_recent("Brom") == []


def test_chat_end_of_input_ends_cleanly(data_dir, fake_client):
    """Ctrl-D (end of input) finishes the chat without a traceback."""
    save_npc(data_dir)
    result = run("chat", "Brom", input="hello\n")
    assert result.exit_code == 0
    assert "Traceback" not in result.output
    assert "Goodbye from Brom" in result.output


def test_chat_unknown_npc(data_dir, fake_client):
    """Chatting with an NPC that does not exist gives a clear error."""
    result = run("chat", "Nobody", input="hi\nquit\n")
    assert result.exit_code != 0
    assert "No NPC named 'Nobody'" in result.output


# --- clear-memory (Feature 3) -------------------------------------------------


def test_clear_memory_empties_history(data_dir):
    """clear-memory wipes the NPC's chat history, confirms, and keeps the profile."""
    save_npc(data_dir)
    memory = NPCMemory(data_dir)
    memory.add_exchange("Brom", Exchange("hi", "grunt", "2026-10-14T23:05:00"))
    result = run("clear-memory", "Brom")
    assert result.exit_code == 0
    assert "Cleared Brom's memory" in result.output
    assert memory.get_recent("Brom") == []
    assert NPCStore(data_dir).exists("Brom")


def test_clear_memory_with_no_history(data_dir):
    """Clearing an NPC nobody has talked to yet is fine."""
    save_npc(data_dir)
    assert run("clear-memory", "Brom").exit_code == 0


def test_clear_memory_unknown_npc(data_dir):
    """Clearing an NPC that does not exist gives a clear error."""
    result = run("clear-memory", "Nobody")
    assert result.exit_code != 0
    assert "No NPC named 'Nobody'" in result.output


# --- .env file ------------------------------------------------------------------


def test_env_file_supplies_api_key(data_dir, monkeypatch):
    """A .env file in the folder the command runs from provides ANTHROPIC_API_KEY."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (data_dir / ".env").write_text("ANTHROPIC_API_KEY=from-dotenv\n")
    assert run("list-npcs").exit_code == 0
    assert os.environ["ANTHROPIC_API_KEY"] == "from-dotenv"


def test_shell_variable_wins_over_env_file(data_dir, monkeypatch):
    """A key already exported in the shell is not replaced by the .env file."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-shell")
    (data_dir / ".env").write_text("ANTHROPIC_API_KEY=from-dotenv\n")
    run("list-npcs")
    assert os.environ["ANTHROPIC_API_KEY"] == "from-shell"


# --- General ------------------------------------------------------------------


def test_help_lists_all_commands():
    """whoelse --help lists create-npc, list-npcs, talk-to, chat and clear-memory."""
    result = run("--help")
    assert result.exit_code == 0
    for command in ("create-npc", "list-npcs", "talk-to", "chat", "clear-memory"):
        assert command in result.output
