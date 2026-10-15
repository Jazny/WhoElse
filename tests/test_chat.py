"""Tests for npc_dm/chat.py. Avoid real API calls: test the prompt-building parts."""


def test_system_prompt_contains_npc_details():
    """The system prompt should mention the NPC's name, personality, and voice."""
    # TODO: build a prompt for a sample NPC and assert the details appear in it
    pass


def test_build_messages_order(tmp_path):
    """History comes first (user, assistant, user, assistant...), new message last."""
    # TODO: add exchanges to memory, call build_messages, check order and roles
    pass
