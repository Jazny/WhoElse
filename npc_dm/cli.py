"""Command-line interface. Wires the commands to NPCStore, NPCMemory, NPCChat."""

import anthropic
import click

from npc_dm.chat import NPCChat
from npc_dm.config import DATA_DIR
from npc_dm.memory import NPCMemory
from npc_dm.models import NPC
from npc_dm.storage import NPCStore


def _store() -> NPCStore:
    return NPCStore(DATA_DIR)


def _make_chat() -> NPCChat:
    """Build the chat object. Tests replace this to avoid real API calls."""
    return NPCChat(NPCMemory(DATA_DIR))


def _load_npc(name: str) -> NPC:
    """Load an NPC by name, or stop with a friendly error if there isn't one."""
    try:
        return _store().load(name)
    except (FileNotFoundError, ValueError):
        raise click.ClickException(
            f"No NPC named {name!r}. See saved NPCs with: whoelse list-npcs"
        ) from None


def _split(text: str) -> list[str]:
    """Turn "a; b;; c" into ["a", "b", "c"]."""
    return [part.strip() for part in text.split(";") if part.strip()]


@click.group()
def main():
    """NPC DM Helper: create NPCs and talk to them in character."""


@main.command("create-npc")
def create_npc():
    """Create a new NPC by answering a few prompts (Feature 1)."""
    store = _store()
    name = click.prompt("Name").strip()
    # Check the name straight away so the DM doesn't answer every prompt for nothing.
    try:
        taken = store.exists(name)
    except ValueError as error:
        raise click.ClickException(str(error)) from None
    if taken:
        raise click.ClickException(
            f"An NPC named {name!r} already exists. Overwriting is not supported."
        )

    personality = click.prompt("Personality")
    voice = click.prompt("Voice")
    backstory = click.prompt("Backstory (optional)", default="", show_default=False)
    motivations = click.prompt(
        "Motivations, separated by ; (optional)", default="", show_default=False
    )
    secrets = click.prompt(
        "Secrets, separated by ; (optional)", default="", show_default=False
    )

    npc = NPC(
        name=name,
        personality=personality.strip(),
        voice=voice.strip(),
        backstory=backstory.strip(),
        motivations=_split(motivations),
        secrets=_split(secrets),
    )
    try:
        store.save(npc)
    except FileExistsError as error:
        raise click.ClickException(str(error)) from None
    click.echo(f"Saved {npc.name}.")


@main.command("list-npcs")
def list_npcs():
    """Show every saved NPC with a one-line summary (Feature 4)."""
    npcs = _store().list_all()
    if not npcs:
        click.echo("No NPCs yet. Create one with: whoelse create-npc")
        return
    # Secrets are left out on purpose: this list is safe to show at the table.
    for npc in npcs:
        click.echo(f"{npc.name}: {npc.personality}")


@main.command("talk-to")
@click.argument("npc_name")
@click.argument("message")
def talk_to(npc_name: str, message: str):
    """Send MESSAGE to the NPC called NPC_NAME and print the reply (Feature 2)."""
    npc = _load_npc(npc_name)
    try:
        reply = _make_chat().talk(npc, message)
    except (RuntimeError, anthropic.AnthropicError) as error:
        raise click.ClickException(str(error)) from None
    click.echo(reply)


@main.command("chat")
@click.argument("npc_name")
def chat(npc_name: str):
    """Start a conversation with NPC_NAME. Type "quit" to finish (Feature 2)."""
    npc = _load_npc(npc_name)
    chat_turns = _make_chat()
    click.echo(f"Talking to {npc.name}. Type 'quit' to finish.")
    while True:
        try:
            message = click.prompt("You", prompt_suffix=" > ", default="", show_default=False)
        except (click.Abort, EOFError):
            # Ctrl-C or Ctrl-D ends the conversation the same way "quit" does.
            click.echo("")
            break
        message = message.strip()
        if message.lower() == "quit":
            break
        if not message:
            continue
        try:
            reply = chat_turns.talk(npc, message)
        except (RuntimeError, anthropic.AnthropicError) as error:
            # Keep the conversation going: one failed turn is not the end of it.
            click.echo(f"Error: {error}")
            continue
        click.echo(f"{npc.name}: {reply}")
    click.echo(f"Goodbye from {npc.name}.")


@main.command("clear-memory")
@click.argument("npc_name")
def clear_memory(npc_name: str):
    """Erase an NPC's history to start a fresh session (Feature 3)."""
    npc = _load_npc(npc_name)
    NPCMemory(DATA_DIR).clear(npc.name)
    click.echo(f"Cleared {npc.name}'s memory.")


if __name__ == "__main__":
    main()
