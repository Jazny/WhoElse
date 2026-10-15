# NPC DM Helper (Proof of Concept Skeleton)

A command-line tool that lets a Dungeons & Dragons Dungeon Master create NPCs
and talk to them in character, powered by Claude. Each NPC remembers what has
been said to it.

This is a **skeleton only**. Every function has a docstring explaining what it
should do, and a `TODO` where the real code goes.

## The four features

1. **Create an NPC**: save a name, personality, voice, motivations, and secrets
2. **Talk to an NPC**: send a message, get an in-character reply from Claude
3. **NPC memory**: each NPC remembers its past exchanges
4. **List and switch NPCs**: see all NPCs, pick which one to talk to

## Folder layout

```
npc_dm_helper/
├── README.md              <- you are here
├── pyproject.toml         <- project metadata and dependencies
├── npc_dm/                <- the actual code
│   ├── __init__.py
│   ├── config.py          <- settings (model name, folders, history limit)
│   ├── models.py          <- data classes: NPC, Exchange
│   ├── storage.py         <- NPCStore: saves/loads NPC profiles (Feature 1, 4)
│   ├── memory.py          <- NPCMemory: saves/loads chat history (Feature 3)
│   ├── chat.py            <- NPCChat: builds prompt, calls Claude (Feature 2)
│   └── cli.py             <- command-line commands (ties it all together)
├── npcs/                  <- NPC profiles and histories live here as JSON
│   └── example_tavern_keeper.json
└── tests/                 <- one test file per module
    ├── test_models.py
    ├── test_storage.py
    ├── test_memory.py
    └── test_chat.py
```

## How the pieces connect

```
cli.py  ──>  NPCStore   (create, load, list NPCs)
   │
   └──────>  NPCChat    (talk to an NPC)
                 │
                 ├──>  NPCMemory  (read/write past exchanges)
                 └──>  Claude API (generate the reply)
```

`models.py` is used by everything. `config.py` holds shared settings.

## Suggested build order

1. `models.py` (two small data classes)
2. `storage.py` (save/load JSON) and test it
3. `memory.py` (append/read JSON) and test it
4. `chat.py` (prompt building, then the real API call)
5. `cli.py` (wire the commands to the classes above)

## Planned commands

```
npc-dm create-npc            # prompts for name, personality, voice
npc-dm list-npcs             # shows all saved NPCs
npc-dm talk-to "Brom" "The party asks about the noises in the cellar"
npc-dm clear-memory "Brom"   # wipe that NPC's history
```

## Setup (once the code exists)

```
pip install -e .
export ANTHROPIC_API_KEY=your-key-here
```
