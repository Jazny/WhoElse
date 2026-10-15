"""Tests for npc_dm/storage.py. Use pytest's tmp_path so no real files are touched."""

import pytest

from npc_dm.models import NPC
from npc_dm.storage import NPCStore


def make_npc(name: str = "Brom") -> NPC:
    return NPC(
        name=name,
        personality="Grumpy tavern keeper.",
        voice="Gruff.",
        backstory="Retired soldier who bought the tavern.",
        motivations=["Keep the tavern open"],
        secrets=["Hides smuggled goods in the cellar"],
    )


def test_save_then_load(tmp_path):
    """Saving an NPC and loading it back gives the same NPC."""
    store = NPCStore(tmp_path)
    npc = make_npc()
    store.save(npc)
    assert store.load("Brom") == npc


def test_list_all(tmp_path):
    """list_all returns every saved NPC and skips history files."""
    store = NPCStore(tmp_path)
    store.save(make_npc("Brom"))
    store.save(make_npc("Old Mira"))
    (tmp_path / "brom_history.json").write_text("[]")
    assert [npc.name for npc in store.list_all()] == ["Brom", "Old Mira"]


def test_exists(tmp_path):
    """exists is False before saving and True after."""
    store = NPCStore(tmp_path)
    assert not store.exists("Brom")
    store.save(make_npc())
    assert store.exists("Brom")


def test_load_missing_raises(tmp_path):
    """Loading an NPC that was never saved raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        NPCStore(tmp_path).load("Nobody")


def test_path_for_is_safe(tmp_path):
    """Names become lowercase slugs that stay inside the data folder."""
    store = NPCStore(tmp_path)
    assert store._path_for("Old Brom") == tmp_path / "old_brom.json"
    assert store._path_for("../../etc/passwd").parent == tmp_path


def test_creates_data_folder(tmp_path):
    """The data folder is created if it does not exist yet."""
    NPCStore(tmp_path / "new_folder")
    assert (tmp_path / "new_folder").is_dir()


def test_save_overwrites_existing(tmp_path):
    """Saving an NPC with the same name replaces the old profile."""
    store = NPCStore(tmp_path)
    store.save(make_npc())
    updated = make_npc()
    updated.personality = "Cheerful, now that the debt is paid."
    store.save(updated)
    assert store.load("Brom") == updated
    assert len(store.list_all()) == 1


def test_load_is_case_insensitive(tmp_path):
    """"brom" and "BROM" load the NPC saved as "Brom"."""
    store = NPCStore(tmp_path)
    store.save(make_npc())
    assert store.load("brom") == store.load("BROM") == make_npc()


def test_list_all_empty(tmp_path):
    """An empty data folder gives an empty list."""
    assert NPCStore(tmp_path).list_all() == []
