"""NPCMemory: remembers what was said to each NPC. Covers Feature 3."""

from pathlib import Path

from npc_dm.config import DATA_DIR, MAX_HISTORY_EXCHANGES
from npc_dm.models import Exchange


class NPCMemory:
    """Keeps one history file per NPC.

    Example: Brom's history is saved as npcs/brom_history.json
    Profiles (storage.py) and histories (this file) are kept separate on purpose.
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir

    def add_exchange(self, npc_name: str, exchange: Exchange) -> None:
        """Append one exchange to the end of the NPC's history."""
        # TODO: load existing history, append the new exchange, save it back
        raise NotImplementedError

    def get_recent(
        self, npc_name: str, limit: int = MAX_HISTORY_EXCHANGES
    ) -> list[Exchange]:
        """Return the most recent exchanges, oldest first, up to `limit`."""
        # TODO: load history and return only the last `limit` items
        raise NotImplementedError

    def clear(self, npc_name: str) -> None:
        """Delete the NPC's history to start a fresh session."""
        # TODO: remove or empty the history file
        raise NotImplementedError

    def _path_for(self, npc_name: str) -> Path:
        """Turn an NPC name into a history file path, e.g. npcs/brom_history.json"""
        # TODO: same naming idea as NPCStore, but ending in _history.json
        raise NotImplementedError
