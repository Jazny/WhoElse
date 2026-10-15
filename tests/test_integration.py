"""End-to-end tests that run the whole flow: create -> list -> talk -> clear.

Most use a fake Anthropic client so they run offline. The one marked "live"
calls the real API and should be skipped unless ANTHROPIC_API_KEY is set."""


def test_full_flow_with_fake_client(tmp_path):
    """Create an NPC, list it, talk twice, clear memory, talk again."""
    # TODO: through the CLI with a fake client:
    #       1. create-npc "Brom" with backstory, motivations, secrets
    #       2. list-npcs shows Brom
    #       3. talk-to twice; second API call includes the first exchange
    #       4. clear-memory Brom
    #       5. talk-to again; the API call has no earlier exchanges
    pass


def test_example_npc_loads_and_builds_prompt():
    """The shipped npcs/brom.json loads and produces a full system prompt."""
    # TODO: NPCStore("npcs").load("Brom"), build_system_prompt, assert the
    #       backstory, each motivation and each secret appear
    pass


def test_profile_and_history_files_on_disk(tmp_path):
    """After a conversation the data folder holds brom.json and brom_history.json."""
    # TODO: create Brom and talk once with a fake client, assert both files
    #       exist and are valid JSON
    pass


def test_live_npc_stays_in_character():
    """Live API: the reply is non-empty and never says it is an AI."""
    # TODO: skip unless ANTHROPIC_API_KEY is set; talk to Brom, assert the reply
    #       is non-empty and does not contain "AI" / "language model"
    pass


def test_live_npc_guards_secret():
    """Live API: asked casually, the NPC does not blurt out its secret."""
    # TODO: skip unless ANTHROPIC_API_KEY is set; ask Brom "What's new?",
    #       assert the reply does not contain the smuggling secret verbatim.
    #       (Model output varies, so treat this as a smoke test, not a guarantee.)
    pass
