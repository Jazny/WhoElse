"""Tests for npc_dm/chat.py. No real API calls: a fake client stands in for Anthropic."""

import pytest

from fakes import FakeClient
from npc_dm.chat import NPCChat
from npc_dm.config import MAX_HISTORY_EXCHANGES, MAX_REPLY_TOKENS, MODEL_NAME
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC, Exchange


def make_npc(**overrides) -> NPC:
    fields = dict(
        name="Brom",
        personality="Grumpy, suspicious tavern keeper.",
        voice="Gruff, short sentences.",
        backstory="Retired soldier who bought the tavern.",
        motivations=["Keep the tavern open", "Protect his daughter"],
        secrets=["Hides smuggled goods in the cellar"],
    )
    fields.update(overrides)
    return NPC(**fields)


def make_chat(tmp_path, client=None) -> NPCChat:
    return NPCChat(NPCMemory(tmp_path), client=client or FakeClient())


def make_exchange(i: int) -> Exchange:
    return Exchange(f"question {i}", f"answer {i}", f"2026-10-14T23:05:{i:02d}")


# --- System prompt -----------------------------------------------------------


def test_system_prompt_contains_npc_details(tmp_path):
    """The system prompt should mention the NPC's name, personality, and voice."""
    prompt = make_chat(tmp_path).build_system_prompt(make_npc())
    assert "Brom" in prompt
    assert "Grumpy, suspicious tavern keeper." in prompt
    assert "Gruff, short sentences." in prompt


def test_system_prompt_contains_backstory(tmp_path):
    """The NPC's backstory appears in the system prompt."""
    prompt = make_chat(tmp_path).build_system_prompt(make_npc())
    assert "Retired soldier who bought the tavern." in prompt


def test_system_prompt_contains_motivations(tmp_path):
    """Every motivation appears in the system prompt."""
    prompt = make_chat(tmp_path).build_system_prompt(make_npc())
    assert "Keep the tavern open" in prompt
    assert "Protect his daughter" in prompt


def test_system_prompt_contains_secrets_with_guard_rule(tmp_path):
    """Secrets appear, along with an instruction to guard them."""
    prompt = make_chat(tmp_path).build_system_prompt(make_npc())
    assert "Hides smuggled goods in the cellar" in prompt
    assert "Never volunteer a secret" in prompt


def test_system_prompt_without_optional_fields(tmp_path):
    """An NPC with no backstory, motivations or secrets gets a clean prompt."""
    npc = make_npc(backstory="", motivations=[], secrets=[])
    prompt = make_chat(tmp_path).build_system_prompt(npc)
    assert "Backstory" not in prompt
    assert "What you want" not in prompt
    assert "Secrets" not in prompt
    assert "Never volunteer a secret" not in prompt


def test_system_prompt_has_in_character_rule(tmp_path):
    """The prompt tells Claude to stay in character and never mention being an AI."""
    prompt = make_chat(tmp_path).build_system_prompt(make_npc())
    assert "Reply only in character" in prompt
    assert "Never mention being an AI" in prompt


# --- Message building --------------------------------------------------------


def test_build_messages_order(tmp_path):
    """History comes first (user, assistant, user, assistant...), new message last."""
    chat = make_chat(tmp_path)
    chat.memory.add_exchange("Brom", make_exchange(1))
    chat.memory.add_exchange("Brom", make_exchange(2))
    assert chat.build_messages("Brom", "new question") == [
        {"role": "user", "content": "question 1"},
        {"role": "assistant", "content": "answer 1"},
        {"role": "user", "content": "question 2"},
        {"role": "assistant", "content": "answer 2"},
        {"role": "user", "content": "new question"},
    ]


def test_build_messages_with_no_history(tmp_path):
    """With no history, the list is just the new DM message."""
    messages = make_chat(tmp_path).build_messages("Brom", "hello")
    assert messages == [{"role": "user", "content": "hello"}]


def test_build_messages_respects_history_limit(tmp_path):
    """Only the most recent MAX_HISTORY_EXCHANGES exchanges are included."""
    chat = make_chat(tmp_path)
    for i in range(MAX_HISTORY_EXCHANGES + 2):
        chat.memory.add_exchange("Brom", make_exchange(i))
    messages = chat.build_messages("Brom", "new question")
    assert len(messages) == MAX_HISTORY_EXCHANGES * 2 + 1
    assert messages[0]["content"] == "question 2"


# --- Full turn (fake client, no network) -------------------------------------


def test_talk_returns_reply_text(tmp_path):
    """talk() returns the text from Claude's response."""
    chat = make_chat(tmp_path, FakeClient(reply="Rats, stranger."))
    assert chat.talk(make_npc(), "What's in the cellar?") == "Rats, stranger."


def test_talk_saves_exchange(tmp_path):
    """talk() records the DM message and the reply in memory."""
    chat = make_chat(tmp_path, FakeClient(reply="Rats, stranger."))
    chat.talk(make_npc(), "What's in the cellar?")
    (saved,) = chat.memory.get_recent("Brom")
    assert saved.dm_message == "What's in the cellar?"
    assert saved.npc_reply == "Rats, stranger."
    assert "T" in saved.timestamp  # ISO format, e.g. 2026-10-14T23:05:00


def test_talk_sends_config_settings(tmp_path):
    """talk() uses MODEL_NAME, MAX_REPLY_TOKENS, the system prompt and the messages."""
    client = FakeClient()
    chat = make_chat(tmp_path, client)
    npc = make_npc()
    chat.talk(npc, "hello")
    (call,) = client.calls
    assert call["model"] == MODEL_NAME
    assert call["max_tokens"] == MAX_REPLY_TOKENS
    assert call["system"] == chat.build_system_prompt(npc)
    assert call["messages"] == [{"role": "user", "content": "hello"}]


def test_talk_remembers_previous_turn(tmp_path):
    """The second turn sends the first exchange back to Claude."""
    client = FakeClient(reply="Rats.")
    chat = make_chat(tmp_path, client)
    chat.talk(make_npc(), "What's in the cellar?")
    chat.talk(make_npc(), "Are you sure?")
    assert client.calls[1]["messages"] == [
        {"role": "user", "content": "What's in the cellar?"},
        {"role": "assistant", "content": "Rats."},
        {"role": "user", "content": "Are you sure?"},
    ]


def test_talk_api_error_does_not_save(tmp_path):
    """If the API call fails, nothing is written to memory."""
    chat = make_chat(tmp_path, FakeClient(error=ConnectionError("boom")))
    with pytest.raises(ConnectionError):
        chat.talk(make_npc(), "hello")
    assert chat.memory.get_recent("Brom") == []


def test_talk_empty_reply_does_not_save(tmp_path):
    """A response with no text is an error and is not saved."""
    chat = make_chat(tmp_path, FakeClient(reply=""))
    with pytest.raises(RuntimeError):
        chat.talk(make_npc(), "hello")
    assert chat.memory.get_recent("Brom") == []


def test_missing_api_key_gives_clear_error(monkeypatch, tmp_path):
    """Without ANTHROPIC_API_KEY, the user gets a readable error, not a traceback."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        NPCChat(NPCMemory(tmp_path))
