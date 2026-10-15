"""NPCMemory: remembers what was said to each NPC. Covers Feature 3."""

import json
from pathlib import Path

from npc_dm.config import DATA_DIR, MAX_HISTORY_EXCHANGES
from npc_dm.models import Exchange
from npc_dm.storage import slugify


class NPCMemory:
    """Keeps one history file per NPC.

    Example: Brom's history is saved as npcs/brom_history.json
    Profiles (storage.py) and histories (this file) are kept separate on purpose.
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)

    def add_exchange(self, npc_name: str, exchange: Exchange) -> None:
        """Append one exchange to the end of the NPC's history."""
        history = self._load(npc_name)
        history.append(exchange)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        data = [item.to_dict() for item in history]
        self._path_for(npc_name).write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )

    def get_recent(
        self, npc_name: str, limit: int = MAX_HISTORY_EXCHANGES
    ) -> list[Exchange]:
        """Return the most recent exchanges, oldest first, up to `limit`."""
        if limit <= 0:
            return []
        return self._load(npc_name)[-limit:]

    def clear(self, npc_name: str) -> None:
        """Delete the NPC's history to start a fresh session."""
        self._path_for(npc_name).unlink(missing_ok=True)

    def _load(self, npc_name: str) -> list[Exchange]:
        """Read the full history, or an empty list if there is none yet."""
        path = self._path_for(npc_name)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Exchange.from_dict(item) for item in data]

    def _path_for(self, npc_name: str) -> Path:
        """Turn an NPC name into a history file path, e.g. npcs/brom_history.json"""
        return self.data_dir / f"{slugify(npc_name)}_history.json"
