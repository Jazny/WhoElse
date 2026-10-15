"""Command-line interface. Wires the commands to NPCStore, NPCMemory, NPCChat."""

import click


@click.group()
def main():
    """NPC DM Helper: create NPCs and talk to them in character."""


@main.command("create-npc")
def create_npc():
    """Create a new NPC by answering a few prompts (Feature 1)."""
    # TODO: ask for name, personality, voice with click.prompt
    # TODO: build an NPC, save it with NPCStore, print a confirmation
    raise NotImplementedError


@main.command("list-npcs")
def list_npcs():
    """Show every saved NPC with a one-line summary (Feature 4)."""
    # TODO: use NPCStore.list_all and print name + personality
    raise NotImplementedError


@main.command("talk-to")
@click.argument("npc_name")
@click.argument("message")
def talk_to(npc_name: str, message: str):
    """Send MESSAGE to the NPC called NPC_NAME and print the reply (Feature 2)."""
    # TODO: load the NPC, call NPCChat.talk, print the reply
    raise NotImplementedError


@main.command("clear-memory")
@click.argument("npc_name")
def clear_memory(npc_name: str):
    """Erase an NPC's history to start a fresh session (Feature 3)."""
    # TODO: call NPCMemory.clear and print a confirmation
    raise NotImplementedError


if __name__ == "__main__":
    main()
