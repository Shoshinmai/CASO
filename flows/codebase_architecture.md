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

│   ├── statemanager.py       # Collect system state (active window, apps)

│   └── models.py              # State data structure

│

├── llm/

│   ├── llmclient.py          # Wrapper for LLM calls

│   ├── prompts.py             # Prompt templates (intent, planner, etc.)

│   └── parser.py              # Parse LLM output → structured format

│

├── intent/

│   ├── intentextractor.py    # Extract intent + slots

│   └── slotschema.py         # Define required fields per intent

│

├── clarification/

│   ├── clarifier.py           # Handles missing info logic

│   └── conversationstate.py  # Tracks pending questions / context

│

├── planner/

│   ├── planner.py             # Decide: macro vs tool

│   └── actionschema.py       # Standard action format

│

├── executor/

│   ├── executor.py            # Executes actions

│   ├── toolregistry.py       # Available tools

│   └── tools/

│       ├── openapp.py

│       ├── typetext.py

│       ├── presskey.py

│       └── openurl.py

│

├── macros/

│   ├── macroregistry.py      # List of macros

│   └── basicmacros.py        # e.g., openyoutube, searchgoogle

│

├── feedback/

│   ├── feedbackmanager.py    # Success / failure handling

│   └── errorhandler.py       # Retry / fallback logic

│

├── utils/

│   ├── logger.py              # Logging

│   ├── helpers.py             # Common functions

│   └── delays.py              # Sleep / wait utilities

│

└── tests/                     # (optional for **now)**