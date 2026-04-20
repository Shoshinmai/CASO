# System Architecture:



User Input

&#x20;  ↓

State Awareness

&#x20;  ↓

Intent + Slot Extraction (LLM)

&#x20;  ↓

Check Missing Info

&#x20;  ↓

IF missing:

&#x20;  → Clarification Loop (ask user)

ELSE:

&#x20;  ↓

Planner (Hybrid: macros + tools)

&#x20;  ↓

Executor

&#x20;  ↓

Execution Feedback

