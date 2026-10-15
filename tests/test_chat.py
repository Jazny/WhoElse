"""Tests for npc_dm/chat.py. Avoid real API calls: test the prompt-building parts,
and replace the Anthropic client with a fake when testing talk()."""


# --- System prompt -----------------------------------------------------------


def test_system_prompt_contains_npc_details():
    """The system prompt should mention the NPC's name, personality, and voice."""
    # TODO: build a prompt for a sample NPC and assert the details appear in it
    pass


def test_system_prompt_contains_backstory():
    """The NPC's backstory appears in the system prompt."""
    # TODO: build a prompt for an NPC with a backstory, assert the text appears
    pass


def test_system_prompt_contains_motivations():
    """Every motivation appears in the system prompt."""
    # TODO: build a prompt for an NPC with two motivations, assert both appear
    pass


def test_system_prompt_contains_secrets_with_guard_rule():
    """Secrets appear, along with an instruction to guard them."""
    # TODO: build a prompt for an NPC with a secret, assert the secret appears
    #       and that the prompt tells the NPC not to reveal secrets freely
    pass


def test_system_prompt_without_optional_fields():
    """An NPC with no backstory, motivations or secrets gets a clean prompt."""
    # TODO: build a prompt for an NPC with only name/personality/voice, assert
    #       no empty "Secrets:" or "Motivations:" headings appear
    pass


def test_system_prompt_has_in_character_rule():
    """The prompt tells Claude to stay in character and never mention being an AI."""
    # TODO: assert the prompt contains the in-character / not-an-AI rule
    pass


# --- Message building --------------------------------------------------------


def test_build_messages_order(tmp_path):
    """History comes first (user, assistant, user, assistant...), new message last."""
    # TODO: add exchanges to memory, call build_messages, check order and roles
    pass


def test_build_messages_with_no_history(tmp_path):
    """With no history, the list is just the new DM message."""
    # TODO: call build_messages for a fresh NPC, assert
    #       [{"role": "user", "content": <message>}]
    pass


def test_build_messages_respects_history_limit(tmp_path):
    """Only the most recent MAX_HISTORY_EXCHANGES exchanges are included."""
    # TODO: add MAX_HISTORY_EXCHANGES + 2 exchanges, assert the message list has
    #       MAX_HISTORY_EXCHANGES * 2 + 1 entries and starts at the right exchange
    pass


# --- Full turn (fake client, no network) -------------------------------------


def test_talk_returns_reply_text(tmp_path):
    """talk() returns the text from Claude's response."""
    # TODO: swap chat.client for a fake whose messages.create returns a
    #       response with text "Rats, stranger."; assert talk() returns it
    pass


def test_talk_saves_exchange(tmp_path):
    """talk() records the DM message and the reply in memory."""
    # TODO: with the fake client, call talk(), assert memory.get_recent has one
    #       Exchange with the right dm_message, npc_reply and an ISO timestamp
    pass


def test_talk_sends_config_settings(tmp_path):
    """talk() uses MODEL_NAME, MAX_REPLY_TOKENS, the system prompt and the messages."""
    # TODO: have the fake client record its kwargs, assert model, max_tokens,
    #       system and messages match what build_system_prompt / build_messages give
    pass


def test_talk_api_error_does_not_save(tmp_path):
    """If the API call fails, nothing is written to memory."""
    # TODO: make the fake client raise, assert talk() raises and
    #       memory.get_recent is still empty
    pass


def test_missing_api_key_gives_clear_error(monkeypatch, tmp_path):
    """Without ANTHROPIC_API_KEY, the user gets a readable error, not a traceback."""
    # TODO: monkeypatch.delenv("ANTHROPIC_API_KEY"), create NPCChat, assert a
    #       clear error mentioning ANTHROPIC_API_KEY is raised (on init or talk)
    pass
