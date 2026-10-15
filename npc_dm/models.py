"""Data classes. These hold information and do nothing else."""

from dataclasses import dataclass


@dataclass
class NPC:
    """One non-player character.

    Example:
        NPC(
            name="Brom",
            personality="Grumpy, suspicious tavern keeper who loves gossip.",
            voice="Gruff, short sentences, mutters to himself.",
        )
    """

    name: str
    personality: str
    voice: str

    def to_dict(self) -> dict:
        """Turn this NPC into a plain dict so it can be saved as JSON."""
        # TODO: return a dict with name, personality, voice
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "NPC":
        """Build an NPC from a dict loaded from JSON."""
        # TODO: return cls(...) using the dict's values
        raise NotImplementedError


@dataclass
class Exchange:
    """One back-and-forth: what the DM said, and how the NPC replied."""

    dm_message: str
    npc_reply: str
    timestamp: str  # ISO format text, e.g. "2026-10-14T23:05:00"

    def to_dict(self) -> dict:
        """Turn this exchange into a plain dict so it can be saved as JSON."""
        # TODO: return a dict with dm_message, npc_reply, timestamp
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Exchange":
        """Build an Exchange from a dict loaded from JSON."""
        # TODO: return cls(...) using the dict's values
        raise NotImplementedError
