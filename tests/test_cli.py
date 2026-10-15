"""Tests for npc_dm/cli.py. Use click.testing.CliRunner and point the data folder
at tmp_path (monkeypatch DATA_DIR or run inside runner.isolated_filesystem()).
Never call the real API: replace NPCChat's client with a fake."""


# --- create-npc (Feature 1) ---------------------------------------------------


def test_create_npc_saves_profile(tmp_path):
    """Answering the prompts saves an NPC that NPCStore can load."""
    # TODO: invoke create-npc with input for name, personality, voice,
    #       backstory, motivations, secrets; assert exit code 0, a confirmation
    #       message, and NPCStore.load(name) matches what was typed
    pass


def test_create_npc_optional_fields_can_be_blank(tmp_path):
    """Backstory, motivations and secrets can be skipped with Enter."""
    # TODO: give blank answers for the optional prompts, assert the saved NPC
    #       has "" and [] for them
    pass


def test_create_npc_splits_multiple_motivations_and_secrets(tmp_path):
    """Several motivations or secrets can be entered (e.g. separated by ';')."""
    # TODO: enter "Protect Mira; Pay the debt", assert two motivations saved
    pass


def test_create_npc_existing_name_asks_before_overwriting(tmp_path):
    """Creating an NPC whose name already exists asks before replacing it."""
    # TODO: save "Brom", run create-npc for "Brom" and answer "n", assert the
    #       original profile is unchanged
    pass


# --- list-npcs (Feature 4) ----------------------------------------------------


def test_list_npcs_shows_all(tmp_path):
    """Every saved NPC is listed with its name and personality."""
    # TODO: save two NPCs, invoke list-npcs, assert both names and
    #       personalities appear in the output
    pass


def test_list_npcs_does_not_reveal_secrets(tmp_path):
    """The list is safe to show at the table: secrets never appear."""
    # TODO: save an NPC with a secret, invoke list-npcs, assert the secret text
    #       is not in the output
    pass


def test_list_npcs_empty(tmp_path):
    """With no NPCs, a friendly message suggests create-npc."""
    # TODO: invoke list-npcs on an empty folder, assert exit code 0 and a hint
    pass


# --- talk-to (Feature 2) ------------------------------------------------------


def test_talk_to_prints_reply(tmp_path):
    """talk-to prints the NPC's reply."""
    # TODO: save "Brom", fake the client to return "Rats, stranger.", invoke
    #       talk-to Brom "What's in the cellar?", assert the reply is printed
    pass


def test_talk_to_name_is_case_insensitive(tmp_path):
    """"brom" and "Brom" find the same NPC."""
    # TODO: save "Brom", invoke talk-to brom "...", assert it succeeds
    pass


def test_talk_to_unknown_npc(tmp_path):
    """Talking to an NPC that does not exist gives a clear error."""
    # TODO: invoke talk-to Nobody "hi", assert non-zero exit code and a message
    #       naming the NPC (and suggesting list-npcs), no traceback
    pass


def test_talk_to_remembers_previous_turns(tmp_path):
    """A second talk-to sends the first exchange back to Claude."""
    # TODO: invoke talk-to twice, assert the fake client's second call received
    #       the first DM message and reply in its messages
    pass


# --- clear-memory (Feature 3) -------------------------------------------------


def test_clear_memory_empties_history(tmp_path):
    """clear-memory wipes the NPC's chat history and confirms."""
    # TODO: add an exchange, invoke clear-memory Brom, assert confirmation and
    #       NPCMemory.get_recent("Brom") == []
    pass


def test_clear_memory_unknown_npc(tmp_path):
    """Clearing an NPC that does not exist gives a clear error."""
    # TODO: invoke clear-memory Nobody, assert non-zero exit and a message
    pass


# --- General ------------------------------------------------------------------


def test_help_lists_all_commands():
    """npc-dm --help lists create-npc, list-npcs, talk-to and clear-memory."""
    # TODO: invoke main with --help, assert all four command names appear
    pass
