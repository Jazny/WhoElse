"""NPCStore: saves and loads NPC profiles. Covers Features 1 and 4."""

import json
import re
from pathlib import Path

from npc_dm.config import DATA_DIR
from npc_dm.models import NPC


def slugify(name: str) -> str:
    """Turn an NPC name into a safe file stem, e.g. "Old Brom" -> "old_brom"."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    if not slug:
        raise ValueError(f"NPC name {name!r} has no letters or digits")
    return slug


class NPCStore:
    """Keeps one JSON file per NPC inside the data folder.

    Example: the NPC named "Brom" is saved as npcs/brom.json
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, npc: NPC) -> None:
        """Write a new NPC's profile to its JSON file (Feature 1).

        Overwriting is not allowed for now: if an NPC with this name (or a name
        that maps to the same file, like "brom" and "Brom") already exists,
        raise FileExistsError and leave the saved profile untouched.
        """
        path = self._path_for(npc.name)
        try:
            # Mode "x" creates the file and fails if it already exists, so there
            # is no gap between checking and writing.
            with path.open("x", encoding="utf-8") as file:
                file.write(json.dumps(npc.to_dict(), indent=2) + "\n")
        except FileExistsError:
            raise FileExistsError(
                f"An NPC named {npc.name!r} already exists ({path}); overwriting is not supported"
            ) from None

    def load(self, name: str) -> NPC:
        """Read one NPC from disk by name. Raise an error if not found."""
        path = self._path_for(name)
        if not path.exists():
            raise FileNotFoundError(f"No NPC named {name!r} (looked for {path})")
        return NPC.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_all(self) -> list[NPC]:
        """Return every saved NPC (Feature 4), sorted by name."""
        npcs = [
            NPC.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in self.data_dir.glob("*.json")
            if not path.name.endswith("_history.json")
        ]
        return sorted(npcs, key=lambda npc: npc.name.lower())

    def exists(self, name: str) -> bool:
        """True if an NPC with this name has already been saved."""
        return self._path_for(name).exists()

    def _path_for(self, name: str) -> Path:
        """Turn an NPC name into a safe file path, e.g. "Old Brom" -> npcs/old_brom.json"""
        return self.data_dir / f"{slugify(name)}.json"
