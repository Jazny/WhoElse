"""Tests for npc_dm/memory.py. Use pytest's tmp_path so no real files are touched."""


def test_add_and_get_recent(tmp_path):
    """Added exchanges come back in order."""
    # TODO: add two exchanges, assert get_recent returns them oldest first
    pass


def test_get_recent_respects_limit(tmp_path):
    """Only the last `limit` exchanges are returned."""
    # TODO: add five exchanges, ask for limit=2, assert only the last two
    pass


def test_get_recent_default_limit(tmp_path):
    """Without a limit, get_recent returns at most MAX_HISTORY_EXCHANGES."""
    # TODO: add MAX_HISTORY_EXCHANGES + 3 exchanges, call get_recent with no
    #       limit, assert the length equals MAX_HISTORY_EXCHANGES and the
    #       oldest three were dropped
    pass


def test_get_recent_with_no_history(tmp_path):
    """An NPC nobody has talked to yet has an empty history, not an error."""
    # TODO: call get_recent for a name with no history file, assert []
    pass


def test_clear(tmp_path):
    """After clear, history is empty."""
    # TODO: add an exchange, clear, assert get_recent is empty
    pass


def test_clear_with_no_history(tmp_path):
    """Clearing an NPC that has no history does not raise."""
    # TODO: call clear for a name with no history file, assert no exception
    pass


def test_history_persists_across_instances(tmp_path):
    """History is saved to disk, so a new NPCMemory sees earlier exchanges."""
    # TODO: add an exchange with one NPCMemory(tmp_path), create a second
    #       NPCMemory(tmp_path), assert get_recent returns the same exchange
    pass


def test_histories_are_separate_per_npc(tmp_path):
    """One NPC's exchanges never show up in another NPC's history."""
    # TODO: add an exchange for "Brom" and one for "Mira", assert each
    #       get_recent only returns its own
    pass


def test_history_path_matches_store_naming(tmp_path):
    """History files sit next to profiles: "Old Brom" -> old_brom_history.json"""
    # TODO: assert _path_for("Old Brom") == tmp_path / "old_brom_history.json"
    #       and that a name like "../evil" stays inside tmp_path
    pass


def test_history_file_not_listed_as_npc(tmp_path):
    """NPCStore.list_all ignores history files written by NPCMemory."""
    # TODO: save an NPC with NPCStore, add an exchange with NPCMemory,
    #       assert NPCStore.list_all returns exactly one NPC
    pass


def test_clear_keeps_profile(tmp_path):
    """Clearing memory removes the chat log but not the NPC profile."""
    # TODO: save an NPC, add an exchange, clear, assert NPCStore.exists is
    #       still True
    pass
