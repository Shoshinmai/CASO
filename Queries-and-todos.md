### **Phase 1 codebase architecture:**



caso/

│

├── main.py                     # Entry point (runs the agent loop)

│

├── config/

│   ├── settings.py            # Configs (API keys, thresholds, delays)

│   └── constants.py           # Action names, limits, etc.

│

├── state/

│   ├── state\_manager.py       # Collect system state (active window, apps)

│   └── models.py              # State data structure

│

├── llm/

│   ├── llm\_client.py          # Wrapper for LLM calls

│   ├── prompts.py             # Prompt templates (intent, planner, etc.)

│   └── parser.py              # Parse LLM output → structured format

│

├── intent/

│   ├── intent\_extractor.py    # Extract intent + slots

│   └── slot\_schema.py         # Define required fields per intent

│

├── clarification/

│   ├── clarifier.py           # Handles missing info logic

│   └── conversation\_state.py  # Tracks pending questions / context

│

├── planner/

│   ├── planner.py             # Decide: macro vs tool

│   └── action\_schema.py       # Standard action format

│

├── executor/

│   ├── executor.py            # Executes actions

│   ├── tool\_registry.py       # Available tools

│   └── tools/

│       ├── open\_app.py

│       ├── type\_text.py

│       ├── press\_key.py

│       └── open\_url.py

│

├── macros/

│   ├── macro\_registry.py      # List of macros

│   └── basic\_macros.py        # e.g., open\_youtube, search\_google

│

├── feedback/

│   ├── feedback\_manager.py    # Success / failure handling

│   └── error\_handler.py       # Retry / fallback logic

│

├── utils/

│   ├── logger.py              # Logging

│   ├── helpers.py             # Common functions

│   └── delays.py              # Sleep / wait utilities

│

└── tests/                     # (optional for **now)**

