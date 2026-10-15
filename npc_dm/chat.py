"""NPCChat: builds the prompt and asks Claude for a reply. Covers Feature 2."""

from npc_dm.memory import NPCMemory
from npc_dm.models import NPC


class NPCChat:
    """Handles one conversation turn between the DM and an NPC.

    What happens when the DM talks to an NPC:
        1. Build a system prompt from the NPC's personality and voice
        2. Load the NPC's recent history from NPCMemory
        3. Send system prompt + history + the new DM message to Claude
        4. Save the exchange to NPCMemory
        5. Return the NPC's reply
    """

    def __init__(self, memory: NPCMemory):
        self.memory = memory
        # TODO: create the Anthropic client here (it reads ANTHROPIC_API_KEY)

    def talk(self, npc: NPC, dm_message: str) -> str:
        """Run one full turn (steps 1 to 5 above) and return the NPC's reply."""
        # TODO: call build_system_prompt, build_messages, then the API,
        #       then memory.add_exchange, then return the reply text
        raise NotImplementedError

    def build_system_prompt(self, npc: NPC) -> str:
        """Write the instructions that make Claude act as this NPC.

        Should include the NPC's name, personality, and voice, plus a rule like:
        "Reply only in character. Never mention being an AI."
        """
        # TODO: return a prompt string using npc.name, npc.personality, npc.voice
        raise NotImplementedError

    def build_messages(self, npc_name: str, dm_message: str) -> list[dict]:
        """Turn the saved history plus the new message into API message format.

        Each past exchange becomes two messages:
            {"role": "user", "content": <dm_message>}
            {"role": "assistant", "content": <npc_reply>}
        The new DM message goes last.
        """
        # TODO: use self.memory.get_recent(...) and build the list
        raise NotImplementedError
