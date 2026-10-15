"""Tests for npc_dm/storage.py. Use pytest's tmp_path so no real files are touched."""


def test_save_then_load(tmp_path):
    """Saving an NPC and loading it back gives the same NPC."""
    # TODO: NPCStore(tmp_path), save an NPC, load it, assert equal
    pass


def test_list_all(tmp_path):
    """list_all returns every saved NPC."""
    # TODO: save two NPCs, assert list_all has both
    pass


def test_exists(tmp_path):
    """exists is False before saving and True after."""
    # TODO: check exists before and after save
    pass
