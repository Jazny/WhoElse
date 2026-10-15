"""Tests for npc_dm/memory.py. Use pytest's tmp_path so no real files are touched."""


def test_add_and_get_recent(tmp_path):
    """Added exchanges come back in order."""
    # TODO: add two exchanges, assert get_recent returns them oldest first
    pass


def test_get_recent_respects_limit(tmp_path):
    """Only the last `limit` exchanges are returned."""
    # TODO: add five exchanges, ask for limit=2, assert only the last two
    pass


def test_clear(tmp_path):
    """After clear, history is empty."""
    # TODO: add an exchange, clear, assert get_recent is empty
    pass
