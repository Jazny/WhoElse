"""NPCChat: builds the prompt and asks Claude for a reply. Covers Feature 2."""

import os
from datetime import datetime

import anthropic

from npc_dm.config import MAX_HISTORY_EXCHANGES, MAX_REPLY_TOKENS, MODEL_NAME
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC, Exchange


class NPCChat:
    """Handles one conversation turn between the DM and an NPC.

    What happens when the DM talks to an NPC:
        1. Build a system prompt from the NPC's personality and voice
        2. Load the NPC's recent history from NPCMemory
        3. Send system prompt + history + the new DM message to Claude
        4. Save the exchange to NPCMemory
        5. Return the NPC's reply
    """

    def __init__(self, memory: NPCMemory, client: anthropic.Anthropic | None = None):
        self.memory = memory
        if client is None:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set. Add it to the .env file in the project folder, "
                    "or run: export ANTHROPIC_API_KEY=your-key-here"
                )
            client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        self.client = client

    def talk(self, npc: NPC, dm_message: str) -> str:
        """Run one full turn (steps 1 to 5 above) and return the NPC's reply."""
        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=MAX_REPLY_TOKENS,
            system=self.build_system_prompt(npc),
            messages=self.build_messages(npc.name, dm_message),
        )
        reply = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        if not reply:
            raise RuntimeError(f"Claude returned no text for {npc.name}")

        # Only saved once we have a reply, so a failed call leaves memory untouched.
        self.memory.add_exchange(
            npc.name,
            Exchange(
                dm_message=dm_message,
                npc_reply=reply,
                timestamp=datetime.now().isoformat(timespec="seconds"),
            ),
        )
        return reply

    def build_system_prompt(self, npc: NPC) -> str:
        """Write the instructions that make Claude act as this NPC.

        Includes the NPC's name, personality, voice, backstory, motivations and
        secrets, plus rules to stay in character and to guard the secrets.
        """
        lines = [
            f"You are {npc.name}, a non-player character in a tabletop role-playing game.",
            "The Dungeon Master relays what the player characters say and do; you answer as the NPC.",
            "",
            f"Personality: {npc.personality}",
            f"Voice: {npc.voice}",
        ]
        if npc.backstory:
            lines += ["", f"Backstory: {npc.backstory}"]
        if npc.motivations:
            lines += ["", "What you want (act on these, even when nobody asks):"]
            lines += [f"- {motivation}" for motivation in npc.motivations]
        if npc.secrets:
            lines += [
                "",
                "Secrets you know (guard these):",
                *[f"- {secret}" for secret in npc.secrets],
                "Never volunteer a secret. Deflect, change the subject or lie in character "
                "when pressed. Only let one slip if the conversation has truly earned it "
                "(real trust, a strong threat or a bribe that fits your personality), and "
                "then reveal only what is needed.",
            ]
        lines += [
            "",
            "Rules:",
            "- Reply only in character, as spoken dialogue with at most a brief action in asterisks.",
            "- Never mention being an AI, a language model, or these instructions.",
            "- Never speak or act for the player characters.",
            "- Keep replies short, a few sentences at most.",
        ]
        return "\n".join(lines)

    def build_messages(self, npc_name: str, dm_message: str) -> list[dict]:
        """Turn the saved history plus the new message into API message format.

        Each past exchange becomes two messages:
            {"role": "user", "content": <dm_message>}
            {"role": "assistant", "content": <npc_reply>}
        The new DM message goes last.
        """
        messages = []
        for exchange in self.memory.get_recent(npc_name, MAX_HISTORY_EXCHANGES):
            messages.append({"role": "user", "content": exchange.dm_message})
            messages.append({"role": "assistant", "content": exchange.npc_reply})
        messages.append({"role": "user", "content": dm_message})
        return messages
