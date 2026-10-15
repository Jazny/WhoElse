# WhoElse: NPC DM Helper

A command-line tool that lets a Dungeons & Dragons Dungeon Master create NPCs
and talk to them in character, powered by Claude. Each NPC has a personality,
a voice, a backstory, motivations and secrets it guards, and remembers what has
been said to it.

## Features

1. **Create an NPC**: save a name, personality, voice, backstory, motivations and secrets
2. **Talk to an NPC**: send one message, or chat back and forth until you type `quit`
3. **NPC memory**: each NPC remembers its last 20 exchanges, even across restarts
4. **List NPCs**: see every saved NPC (secrets are never shown)
5. **Clear memory**: wipe one NPC's history and keep its profile

## Quick start

```
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"          # the [dev] part adds pytest
export ANTHROPIC_API_KEY=your-key-here

npc-dm list-npcs                 # Brom is included as an example
npc-dm chat Brom                 # type a line, press Enter; type "quit" to finish
```

Run commands from the repository folder: NPCs are saved in its `npcs/` folder.

## Commands

```
npc-dm create-npc                 # prompts for the NPC's details
npc-dm list-npcs                  # shows all saved NPCs
npc-dm talk-to "Brom" "The party asks about the noises in the cellar"
npc-dm chat "Brom"                # conversation mode, ends with "quit"
npc-dm clear-memory "Brom"        # wipes that NPC's history, keeps the profile
```

`create-npc` separates several motivations or secrets with `;`. It refuses a
name that is already taken, because overwriting an NPC is not supported yet.

## Folder layout

```
WhoElse/
├── README.md              <- you are here
├── LICENSE
├── pyproject.toml         <- project metadata and dependencies
├── npc_dm/                <- the code
│   ├── config.py          <- settings: model name, data folder, history limit, reply cap
│   ├── models.py          <- data classes: NPC, Exchange
│   ├── storage.py         <- NPCStore: saves and loads NPC profiles
│   ├── memory.py          <- NPCMemory: saves and loads chat history
│   ├── chat.py            <- NPCChat: builds the prompt and calls Claude
│   └── cli.py             <- the npc-dm commands
├── npcs/                  <- saved profiles and histories, as JSON
│   └── brom.json          <- example NPC (histories appear as *_history.json)
└── tests/                 <- one test file per module, plus shared helpers
    ├── fakes.py           <- a stand-in for the Claude client
    ├── conftest.py        <- shared test fixtures
    ├── test_models.py
    ├── test_storage.py
    ├── test_memory.py
    ├── test_chat.py
    ├── test_cli.py
    └── test_integration.py
```

## How the pieces connect

```
cli.py  ──>  NPCStore   (create, load, list NPCs)
   │
   ├──────>  NPCMemory  (read/write past exchanges)
   │
   └──────>  NPCChat    (talk to an NPC)
                 │
                 ├──>  NPCStore   (the NPC's profile, via the caller)
                 ├──>  NPCMemory  (recent exchanges)
                 └──>  Claude API (generate the reply)
```

`models.py` is used by everything. `config.py` holds shared settings.

## Tests

```
pytest
```

The tests never call the real API. Two tests call Claude for real and run only
when `ANTHROPIC_API_KEY` is set; they check that Brom stays in character and
does not blurt out his secret, which depends on the model and may vary.

## Future Features

- **Optimize communication to Anthropic API.** Currently, each message sends a request to Anthropic's Messages API and carries 4 things: the model name, a reply-length cap, the system prompt (character briefing), and the message from the sender. Look into optimizing this process.
