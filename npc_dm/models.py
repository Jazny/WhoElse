"""Data classes. These hold information and do nothing else."""

from dataclasses import dataclass, field


@dataclass
class NPC:
    """One non-player character.

    Example:
        NPC(
            name="Brom",
            personality="Grumpy, suspicious tavern keeper who loves gossip.",
            voice="Gruff, short sentences, mutters to himself.",
            motivations=["Keep the tavern profitable", "Protect his daughter"],
            secrets=["He fences stolen goods in the cellar"],
        )

    Motivations are what the NPC wants and acts on. Secrets are things the NPC
    knows but guards, and should only reveal when it makes sense in character.
    """

    name: str
    personality: str
    voice: str
    motivations: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Turn this NPC into a plain dict so it can be saved as JSON."""
        return {
            "name": self.name,
            "personality": self.personality,
            "voice": self.voice,
            "motivations": list(self.motivations),
            "secrets": list(self.secrets),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPC":
        """Build an NPC from a dict loaded from JSON.

        Motivations and secrets are optional, so older profiles still load.
        """
        return cls(
            name=data["name"],
            personality=data["personality"],
            voice=data["voice"],
            motivations=list(data.get("motivations", [])),
            secrets=list(data.get("secrets", [])),
        )


@dataclass
class Exchange:
    """One back-and-forth: what the DM said, and how the NPC replied."""

    dm_message: str
    npc_reply: str
    timestamp: str  # ISO format text, e.g. "2026-10-14T23:05:00"

    def to_dict(self) -> dict:
        """Turn this exchange into a plain dict so it can be saved as JSON."""
        return {
            "dm_message": self.dm_message,
            "npc_reply": self.npc_reply,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Exchange":
        """Build an Exchange from a dict loaded from JSON."""
        return cls(
            dm_message=data["dm_message"],
            npc_reply=data["npc_reply"],
            timestamp=data["timestamp"],
        )
