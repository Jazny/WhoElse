"""NPCStore: saves and loads NPC profiles. Covers Features 1 and 4."""

from pathlib import Path

from npc_dm.config import DATA_DIR
from npc_dm.models import NPC


class NPCStore:
    """Keeps one JSON file per NPC inside the data folder.

    Example: the NPC named "Brom" is saved as npcs/brom.json
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        # TODO: create the data folder if it does not exist yet

    def save(self, npc: NPC) -> None:
        """Write an NPC's profile to its JSON file (Feature 1)."""
        # TODO: use npc.to_dict() and write it to the NPC's file
        raise NotImplementedError

    def load(self, name: str) -> NPC:
        """Read one NPC from disk by name. Raise an error if not found."""
        # TODO: read the file and return NPC.from_dict(...)
        raise NotImplementedError

    def list_all(self) -> list[NPC]:
        """Return every saved NPC (Feature 4)."""
        # TODO: loop over the JSON files in the data folder and load each one.
        #       Skip files ending in "_history.json" (those belong to memory.py)
        raise NotImplementedError

    def exists(self, name: str) -> bool:
        """True if an NPC with this name has already been saved."""
        # TODO: check whether the NPC's file exists
        raise NotImplementedError

    def _path_for(self, name: str) -> Path:
        """Turn an NPC name into a safe file path, e.g. "Old Brom" -> npcs/old_brom.json"""
        # TODO: lowercase the name, swap spaces for underscores, add .json
        raise NotImplementedError
