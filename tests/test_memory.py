"""Tests for npc_dm/memory.py. Use pytest's tmp_path so no real files are touched."""

from npc_dm.config import MAX_HISTORY_EXCHANGES
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC, Exchange
from npc_dm.storage import NPCStore


def make_exchange(i: int = 0) -> Exchange:
    return Exchange(
        dm_message=f"question {i}",
        npc_reply=f"answer {i}",
        timestamp=f"2026-10-14T23:05:{i:02d}",
    )


def test_add_and_get_recent(tmp_path):
    """Added exchanges come back in order."""
    memory = NPCMemory(tmp_path)
    first, second = make_exchange(1), make_exchange(2)
    memory.add_exchange("Brom", first)
    memory.add_exchange("Brom", second)
    assert memory.get_recent("Brom") == [first, second]


def test_get_recent_respects_limit(tmp_path):
    """Only the last `limit` exchanges are returned."""
    memory = NPCMemory(tmp_path)
    exchanges = [make_exchange(i) for i in range(5)]
    for exchange in exchanges:
        memory.add_exchange("Brom", exchange)
    assert memory.get_recent("Brom", limit=2) == exchanges[-2:]


def test_get_recent_default_limit(tmp_path):
    """Without a limit, get_recent returns at most MAX_HISTORY_EXCHANGES."""
    memory = NPCMemory(tmp_path)
    exchanges = [make_exchange(i) for i in range(MAX_HISTORY_EXCHANGES + 3)]
    for exchange in exchanges:
        memory.add_exchange("Brom", exchange)
    recent = memory.get_recent("Brom")
    assert len(recent) == MAX_HISTORY_EXCHANGES
    assert recent == exchanges[3:]


def test_get_recent_zero_or_negative_limit(tmp_path):
    """A limit of 0 or less returns nothing (not the whole history)."""
    memory = NPCMemory(tmp_path)
    for i in range(3):
        memory.add_exchange("Brom", make_exchange(i))
    assert memory.get_recent("Brom", limit=0) == []
    assert memory.get_recent("Brom", limit=-2) == []


def test_get_recent_with_no_history(tmp_path):
    """An NPC nobody has talked to yet has an empty history, not an error."""
    assert NPCMemory(tmp_path).get_recent("Brom") == []


def test_clear(tmp_path):
    """After clear, history is empty."""
    memory = NPCMemory(tmp_path)
    memory.add_exchange("Brom", make_exchange())
    memory.clear("Brom")
    assert memory.get_recent("Brom") == []


def test_clear_with_no_history(tmp_path):
    """Clearing an NPC that has no history does not raise."""
    NPCMemory(tmp_path).clear("Brom")


def test_history_persists_across_instances(tmp_path):
    """History is saved to disk, so a new NPCMemory sees earlier exchanges."""
    exchange = make_exchange()
    NPCMemory(tmp_path).add_exchange("Brom", exchange)
    assert NPCMemory(tmp_path).get_recent("Brom") == [exchange]


def test_add_exchange_creates_data_folder(tmp_path):
    """Adding an exchange works even if the data folder does not exist yet."""
    memory = NPCMemory(tmp_path / "new_folder")
    memory.add_exchange("Brom", make_exchange())
    assert len(memory.get_recent("Brom")) == 1


def test_histories_are_separate_per_npc(tmp_path):
    """One NPC's exchanges never show up in another NPC's history."""
    memory = NPCMemory(tmp_path)
    brom, mira = make_exchange(1), make_exchange(2)
    memory.add_exchange("Brom", brom)
    memory.add_exchange("Mira", mira)
    assert memory.get_recent("Brom") == [brom]
    assert memory.get_recent("Mira") == [mira]


def test_name_lookup_is_case_insensitive(tmp_path):
    """"brom" and "Brom" share one history, matching NPCStore's naming."""
    memory = NPCMemory(tmp_path)
    exchange = make_exchange()
    memory.add_exchange("Brom", exchange)
    assert memory.get_recent("brom") == [exchange]


def test_history_path_matches_store_naming(tmp_path):
    """History files sit next to profiles: "Old Brom" -> old_brom_history.json"""
    memory = NPCMemory(tmp_path)
    assert memory._path_for("Old Brom") == tmp_path / "old_brom_history.json"
    assert memory._path_for("../evil").parent == tmp_path


def test_history_file_not_listed_as_npc(tmp_path):
    """NPCStore.list_all ignores history files written by NPCMemory."""
    store = NPCStore(tmp_path)
    store.save(NPC(name="Brom", personality="Grumpy.", voice="Gruff."))
    NPCMemory(tmp_path).add_exchange("Brom", make_exchange())
    assert [npc.name for npc in store.list_all()] == ["Brom"]


def test_clear_keeps_profile(tmp_path):
    """Clearing memory removes the chat log but not the NPC profile."""
    store = NPCStore(tmp_path)
    store.save(NPC(name="Brom", personality="Grumpy.", voice="Gruff."))
    memory = NPCMemory(tmp_path)
    memory.add_exchange("Brom", make_exchange())
    memory.clear("Brom")
    assert store.exists("Brom")
