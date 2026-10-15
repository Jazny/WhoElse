"""Shared settings. Change values here instead of hunting through the code."""

from pathlib import Path

# Folder where NPC profiles and their histories are saved.
DATA_DIR = Path("npcs")

# Which Claude model generates NPC replies.
MODEL_NAME = "claude-sonnet-5-5"

# How many past exchanges (DM message + NPC reply pairs) get sent back to
# Claude each time. Keeps prompts small and cheap for the proof of concept.
MAX_HISTORY_EXCHANGES = 20

# Cap on the length of each NPC reply.
MAX_REPLY_TOKENS = 400
