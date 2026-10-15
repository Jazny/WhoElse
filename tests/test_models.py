"""Tests for npc_dm/models.py"""

from npc_dm.models import NPC, Exchange


def test_npc_round_trip():
    """An NPC turned into a dict and back should be identical."""
    npc = NPC(
        name="Brom",
        personality="Grumpy tavern keeper.",
        voice="Gruff.",
        motivations=["Keep the tavern open"],
        secrets=["Hides smuggled goods in the cellar"],
    )
    assert NPC.from_dict(npc.to_dict()) == npc


def test_npc_without_motivations_or_secrets_loads():
    """Older profiles without motivations or secrets still load, with empty lists."""
    npc = NPC.from_dict({"name": "Brom", "personality": "Grumpy.", "voice": "Gruff."})
    assert npc.motivations == []
    assert npc.secrets == []


def test_exchange_round_trip():
    """An Exchange turned into a dict and back should be identical."""
    exchange = Exchange(
        dm_message="What's in the cellar?",
        npc_reply="Rats, stranger. Just rats.",
        timestamp="2026-10-14T23:05:00",
    )
    assert Exchange.from_dict(exchange.to_dict()) == exchange
