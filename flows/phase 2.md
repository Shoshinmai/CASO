

# **Phase-2 Architectural design**



##### **User Input**

##### &#x20;  **↓**

##### **State Collector**

##### &#x20;  **↓**

##### **LangGraph Orchestrator**

##### &#x20;  **│**

##### &#x20;  **├── Intent / Interpreter Node**

##### &#x20;  **│**

##### &#x20;  **├── Clarifier Node**

##### &#x20;  **│      └─(if ambiguity)→ user loop**

##### &#x20;  **│**

##### &#x20;  **├── Planner Node**

##### &#x20;  **│**

##### &#x20;  **├── Critic / Plan Validator Node**

##### &#x20;  **│      ├─ EXECUTE**

##### &#x20;  **│      └─ REVISE\_PLAN → Planner**

##### &#x20;  **│**

##### &#x20;  **├── Skill Router Node**

##### &#x20;  **│      ├─ Existing Skill**

##### &#x20;  **│      └─ (future) Coding Agent**

##### &#x20;  **│**

##### &#x20;  **├── Executor Node**

##### &#x20;  **│**

##### &#x20;  **├── Feedback Evaluator**

##### &#x20;  **│      ├─ Success → Done**

##### &#x20;  **│      └─ Failure → Replan**

##### &#x20;  **│**

##### &#x20;  **└── Memory (later in phase)**

