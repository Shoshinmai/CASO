# CASO Terminal Agent — Prototype 3 Design Record

> **Status:** Design baseline before Prototype 3 implementation  
> **Repository:** `Shoshinmai/CASO`  
> **Branch:** `domain-expansion/knowledge-and-self-improvement-design`  
> **Scope:** `agents/terminal`  
> **Important:** Terminal Agent is a **subagent of CASO**, not CASO itself.

---

## 0. Purpose of This Document

This document is the living design record for **Terminal Agent Prototype 3**.

Its purpose is to preserve:

- why Prototype 3 exists,
- the problem we are solving,
- research/design principles established before implementation,
- architectural requirements and invariants,
- the design decisions made in Steps 1–5,
- decisions intentionally left open,
- implementation discoveries,
- changes to the architecture as implementation progresses,
- and future design decisions.

This document should be **updated as the implementation teaches us more**.

The design is not considered immutable. Steps 1–5 represent our current architectural hypothesis. Implementation and testing may refine the boundaries.

---

# 1. Context — What Came Before Prototype 3

## 1.1 Terminal Agent vs CASO

The Terminal Agent is a **subagent of CASO**.

It is responsible for terminal-oriented agent work such as:

- inspecting codebases,
- reading files,
- running terminal tools,
- investigating repositories,
- executing tasks,
- reasoning about discovered information,
- and eventually producing rich outputs/reports.

Prototype 3 is therefore a **Terminal Agent architecture effort**, not a redesign of CASO as a whole.

---

## 1.2 Prototype 2

Prototype 2 established a functioning runtime/execution architecture.

The important conclusion from Prototype 2 was:

> **The runtime flow and execution architecture are healthy.**

The latest end-to-end testing established that the runtime itself should not be redesigned merely because the representation of internal state/memory is too raw for user-facing output.

That representation issue was deliberately deferred to a later output/presentation layer.

### Prototype 2 principle

**Do not destabilize the healthy runtime to solve a representation problem.**

Prototype 3 must therefore build on top of the existing execution/runtime foundation rather than replacing it.

---

# 2. The Problem That Initiated Prototype 3

The Terminal Agent currently relies heavily on **active/working memory as the information available to its reasoning process**.

This works for small tasks, but becomes problematic for larger investigation/reporting tasks.

Example:

> User asks the Terminal Agent to produce a detailed report about a codebase.

The agent may need to:

1. search the repository,
2. inspect many files,
3. understand relationships between components,
4. compare implementations,
5. inspect tests,
6. trace execution,
7. revisit earlier discoveries,
8. synthesize the information,
9. produce a report.

The problem is that the agent cannot simply keep all of this rich information inside its immediate context.

A simplified representation of the existing problem is:

```text
Environment
    ↓
Tools / File Reads
    ↓
Rich Information
    ↓
Active / Working Memory
    ↓
Context limitations
    ↓
Information becomes unavailable or overly compressed
```

This creates the fundamental Prototype 3 problem:

> **How can the Terminal Agent retain rich information, progressively process it into richer understanding, retrieve it later, and use it for reasoning without requiring the entire investigation to remain inside the immediate context?**

---

# 3. Core Goal of Prototype 3

Prototype 3 should allow the Terminal Agent to:

```text
Acquire information
      ↓
Retain information
      ↓
Process information
      ↓
Build understanding
      ↓
Preserve relationships/provenance
      ↓
Retrieve relevant information later
      ↓
Reconstruct useful working context
      ↓
Reason over it
      ↓
Continue investigating when necessary
```

The core success condition is:

> **The agent can investigate something larger than its immediate context, retain what it learned in a structured form, forget it from immediate working context, retrieve it later, and continue reasoning from the retrieved information.**

---

# 4. Research Before Architecture

Before designing Prototype 3, research was performed into how modern coding/agent systems approach large-context codebase understanding.

The research included systems and discussions around:

- Cursor codebase indexing,
- Claude-style agent workflows,
- Codex-style repository interaction,
- codebase indexing and retrieval,
- search-oriented agent workflows,
- persistent/contextual knowledge,
- and Prime Agent/self-improvement concepts.

Specific research links were also examined, including:

- Towards Data Science — Cursor codebase indexing
- Cursor — secure codebase indexing
- Medium — Cursor indexing large codebases
- LinkedIn discussion on codebase indexing
- YouTube discussions about Cursor/codebase understanding
- X/article discussion related to Cursor/indexing
- Prime Agent related articles/documentation

The research was used as **input to design principles**, not as a blueprint to copy.

---

# 5. Design Principles Extracted From Research

The following principles became the basis for Prototype 3.

## 5.1 Do not treat the entire codebase as one context

The agent should not attempt to put the entire repository into its active context.

Instead:

```text
Repository
   ↓
Information acquisition
   ↓
Structured representations
   ↓
Relevant retrieval
   ↓
Working context
```

---

## 5.2 Search/retrieve information when needed

The agent should be able to retrieve relevant information rather than relying solely on what happened to remain in active memory.

This creates a distinction between:

- information that exists,
- information that is relevant,
- and information currently visible to the model.

---

## 5.3 Working context is not the same as knowledge

The immediate context should be treated as a **working representation**, not the permanent source of truth.

This is one of the most important Prototype 3 principles.

```text
Persistent Information
        ↓
Context Assembly
        ↓
Working Context
        ↓
LLM
```

---

## 5.4 Progressive synthesis

Raw information should be progressively transformed into more useful representations.

Conceptually:

```text
Raw Evidence
     ↓
Finding
     ↓
Relationship
     ↓
Understanding
     ↓
Knowledge
```

The agent should be able to build richer information from previously acquired information.

---

## 5.5 Preserve provenance

Derived understanding should remain traceable to the information that supports it.

Example:

```text
Understanding U1
    ↓ supported by
Finding F1
Finding F2
    ↓ derived from
Evidence E1
Evidence E2
```

This allows the agent to verify and refine its own understanding.

---

## 5.6 Retrieval and reasoning should be separate

Retrieval answers:

> What information might be relevant?

Context assembly answers:

> What information should the model actually see?

Reasoning answers:

> What does the information mean?

These should remain separate responsibilities.

---

## 5.7 Self-improvement should be separate from task knowledge

Task knowledge describes the environment/project.

Self-improvement knowledge describes how the agent itself can work better.

```text
Task Knowledge
    → What I know about the task/project

Agent Knowledge
    → What I know about how to operate better
```

---

## 5.8 Self-improvement should not destabilize task execution

Self-improvement should operate as a separate loop and should not constantly interrupt the active task.

Experience can be collected during execution and reflected upon at appropriate boundaries.

---

## 5.9 Execution and cognition should be separated

Execution answers:

> How do I perform an action?

Cognition/information processing answers:

> What did I learn from that action, and what does it mean?

Prototype 3 should not turn the executor into a knowledge manager.

---

## 5.10 Storage and intelligence should be separated

The information store should not decide what information means.

Likewise, the intelligence layer should not depend on a specific storage implementation.

---

# 6. Architectural Requirements / Invariants

These principles were converted into architectural requirements.

## Requirement 1 — Runtime preservation

Prototype 3 must not require restructuring the healthy Prototype 2 execution runtime.

---

## Requirement 2 — Working-memory limitation must not imply knowledge loss

Information leaving active/working context must remain recoverable when appropriate.

---

## Requirement 3 — Evidence must have a durable boundary

Tool/environment results should enter the information system through a structured evidence boundary.

---

## Requirement 4 — Information must be progressively processable

The architecture must support transformations such as:

```text
Evidence
→ Finding
→ Understanding
→ Knowledge
```

---

## Requirement 5 — Provenance must survive transformation

Derived information must remain traceable to supporting evidence.

---

## Requirement 6 — Retrieval must be independent of working memory

The agent must be able to retrieve previously retained information without depending on that information still being present in active memory.

---

## Requirement 7 — Context must be constructed

The model should receive a context assembled for the current goal/question rather than directly consuming the entire information system.

---

## Requirement 8 — Investigation must be question-driven

Information acquisition should be driven by unresolved information needs rather than indiscriminate exploration.

---

## Requirement 9 — Retrieval should precede redundant investigation

When useful retained information already exists, the system should attempt to retrieve it before reacquiring the same information.

---

## Requirement 10 — Knowledge must evolve

New evidence must be capable of:

- confirming,
- refining,
- contradicting,
- superseding,
- or invalidating existing knowledge.

---

## Requirement 11 — Task knowledge and agent knowledge are distinct

Knowledge about the project/task must remain conceptually separate from knowledge about improving the agent's own behavior.

---

## Requirement 12 — Self-improvement is isolated

Self-improvement must not become a source of instability for the active task execution loop.

---

# 7. Step 1 — Lifecycle

The first architectural step established the high-level lifecycle.

The Terminal Agent should move through an iterative cycle:

```text
Goal
 ↓
Current understanding
 ↓
Identify information need
 ↓
Retrieve existing information
 ↓
If insufficient → investigate
 ↓
Acquire evidence
 ↓
Process evidence
 ↓
Update understanding
 ↓
Build working context
 ↓
Reason
 ↓
Identify next information need
 ↓
Repeat
 ↓
Produce result
```

This means the agent should not be modeled as:

```text
Plan once
→ execute everything
→ answer
```

Instead it should be capable of iterative information acquisition and reasoning.

---

# 8. Step 2 — Information Model

The information architecture was conceptually divided into levels.

## 8.1 Evidence

Raw information acquired from the environment.

Examples:

- file contents,
- terminal output,
- search results,
- test output,
- artifacts,
- execution results.

Evidence should retain provenance.

---

## 8.2 Finding

A meaningful observation derived from evidence.

Example:

```text
Evidence:
Several files mutate runtime state.

Finding:
Runtime state mutation is centralized through a particular boundary.
```

---

## 8.3 Relationship

A connection between information entities.

Examples:

```text
Component A → calls → Component B

Finding F1 → supports → Understanding U1

File A → implements → Component B
```

Relationships are important because codebase understanding is not only a collection of independent facts.

---

## 8.4 Understanding

A synthesized representation built from findings, relationships, and evidence.

Example:

```text
Understanding:
Task execution is coordinated by X, while state mutation is
centralized through Y and reconciliation is handled by Z.
```

---

## 8.5 Knowledge

Information considered useful enough to retain for future retrieval.

Knowledge may be:

- task-scoped,
- project-scoped,
- or eventually more durable/generalized.

---

## 8.6 Working Context

A temporary representation assembled for the current reasoning step.

Working Context is **not authoritative storage**.

It is a projection of relevant information.

---

## 8.7 Experience

Information about what happened while the agent operated.

Examples:

- successful strategy,
- failed strategy,
- repeated mistake,
- recovery pattern,
- inefficient investigation path,
- useful tool-selection pattern.

---

## 8.8 Agent Knowledge

Knowledge derived from experience that can improve future agent behavior.

```text
Experience
    ↓
Reflection
    ↓
Improvement candidate
    ↓
Evaluation
    ↓
Agent Knowledge
```

---

# 9. Step 3 — Operations

The information system needs operations rather than only passive storage.

Conceptual operations identified:

```text
Acquire
Normalize
Extract
Derive
Relate
Synthesize
Validate
Retain
Retrieve
Refine
Invalidate
Supersede
Compress
Archive
Reflect
Generalize
Evaluate
```

These operations should not necessarily become one class per operation.

They are architectural responsibilities.

---

# 10. Step 4 — Architectural Responsibilities

The responsibilities were divided into domains.

## 10.1 Execution Domain

Responsible for:

- task execution,
- runtime state,
- tools,
- workers,
- orchestration,
- reconciliation.

Prototype 2 owns this foundation.

---

## 10.2 Evidence Acquisition

Responsible for turning environment/tool outputs into structured evidence.

```text
Tool
 ↓
Tool Result
 ↓
Evidence
```

---

## 10.3 Information Processing

Responsible for transforming evidence into:

- findings,
- relationships,
- understanding.

---

## 10.4 Knowledge Management

Responsible for:

- retaining,
- refining,
- promoting,
- invalidating,
- superseding,
- archiving information.

---

## 10.5 Information Storage

Infrastructure for retaining and retrieving information.

The storage technology is deliberately not fixed yet.

---

## 10.6 Retrieval Engine

Responsible for finding information relevant to the current goal/question.

---

## 10.7 Context Builder

Responsible for:

- selection,
- prioritization,
- ordering,
- compression,
- deduplication,
- relationship preservation,
- context budgeting.

---

## 10.8 Working Memory

The current working representation available for reasoning.

It should not be treated as the complete knowledge system.

---

## 10.9 Validation / Reconciliation of Knowledge

Responsible for checking new evidence against existing understanding.

Possible outcomes:

```text
confirm
refine
contradict
invalidate
```

---

## 10.10 Experience Collector

Captures experience about agent operation.

---

## 10.11 Reflection / Self-Improvement

Transforms experience into possible reusable improvements.

---

## 10.12 Agent Knowledge

Retains validated improvements to the agent's behavior.

---

# 11. Step 5 — Control & Data Flow

The architectural control model introduced an **Agent Control Loop**.

The Agent Control Loop is the top-level cognitive orchestrator.

It coordinates domains but does not own their internal logic.

---

## 11.1 High-level control flow

```text
Goal
 ↓
Agent Control
 ↓
Identify current information/reasoning need
 ↓
Retrieve
 ↓
 ├── sufficient → Context
 │
 └── insufficient → Investigation
                         ↓
                     Execution
                         ↓
                      Evidence
                         ↓
                   Information
                    Processing
                         ↓
                     Knowledge
                         ↓
                      Context
                         ↓
                   Working Memory
                         ↓
                         LLM
                         ↓
                next decision/action
```

---

## 11.2 Investigation Loop

```text
Question
 ↓
Acquire evidence
 ↓
Evaluate evidence
 ↓
Enough?
 ├── No → investigate more
 └── Yes → resolve question
```

Investigation should be question-driven.

---

## 11.3 Knowledge Loop

```text
Evidence
 ↓
Findings
 ↓
Relationships
 ↓
Understanding
 ↓
Validation
 ↓
Retention
```

The loop should not necessarily run after every individual tool call. Meaningful batches/boundaries may be processed together.

---

## 11.4 Retrieval Loop

```text
Current Question
 ↓
Retrieval Query
 ↓
Relevant information
 ↓
Relevance filtering
 ↓
Context Builder
```

If retrieval is insufficient:

```text
Retrieval
 ↓
insufficient
 ↓
Investigation
```

---

## 11.5 Reasoning Loop

```text
Context
 ↓
LLM
 ↓
Information need
 ↓
Retrieve / investigate
 ↓
New Context
 ↓
LLM
```

This allows iterative reasoning.

---

## 11.6 Self-Improvement Loop

```text
Execution
 ↓
Experience
 ↓
Reflection
 ↓
Improvement Candidate
 ↓
Evaluation
 ↓
Agent Knowledge
 ↓
Future behavior
```

Self-improvement should preferably not block the main task unnecessarily.

---

# 12. Control vs Execution

A critical boundary established in Step 5:

```text
Decision
   ≠
Execution
```

The Agent Control Loop can decide:

> "Inspect the executor implementation."

But the existing Prototype 2 runtime performs the action.

```text
Agent Control
 ↓
Action Request
 ↓
Prototype 2 Runtime
 ↓
Tool Execution
 ↓
Execution Result
 ↓
Information Domain
```

---

# 13. Prototype 2 / Prototype 3 Boundary

Prototype 3 should sit conceptually above the existing execution runtime.

```text
                 PROTOTYPE 3
              Cognitive Layer
                     │
                     ▼
               Agent Control
                     │
                     │ action request
                     ▼
              PROTOTYPE 2
                 Runtime
                     │
                     ▼
                  Tools
                     │
                     ▼
                 Evidence
                     │
                     ▼
              Prototype 3
            Information Layer
```

This preserves the healthy Prototype 2 runtime.

---

# 14. Context as a Projection

One of the strongest design decisions is:

> **Working Memory should become a projection of the information system rather than the authoritative source of information.**

Conceptually:

```text
Information System
       │
       ├── Evidence
       ├── Findings
       ├── Understanding
       ├── Knowledge
       └── Relationships
                │
                ▼
          Context Builder
                │
                ▼
          Working Memory
                │
                ▼
               LLM
```

This directly addresses the original problem.

---

# 15. Controller Responsibility

The Agent Controller is:

> **A conductor, not the entire brain.**

It should:

- coordinate,
- issue requests,
- observe outcomes,
- maintain the high-level task lifecycle.

It should not contain all retrieval, knowledge, investigation, storage, execution, and reflection logic.

---

# 16. Commands and Events

The architecture should use a hybrid communication model.

## Commands

A command asks something to happen.

Example:

```text
"Retrieve information relevant to Question Q1."
```

## Events

An event records something that happened.

Example:

```text
"Evidence E7 was acquired."
```

Conceptually:

```text
Controller
   │
   │ command
   ▼
Subsystem
   │
   │ event
   ▼
System
```

Not every operation needs to be an event. Direct request/response is acceptable where appropriate.

---

# 17. Self-Improvement Design Decision

Prime Agent research raised the question of whether Terminal Agent should also contain a self-improvement mechanism.

Decision:

> **Yes, Prototype 3 should include a self-improvement capability, but it should be a separate domain and should not dominate the first implementation.**

The distinction is:

```text
Task Knowledge
    ↓
What the agent learns about the environment/task

Agent Knowledge
    ↓
What the agent learns about how it should operate
```

Self-improvement is therefore part of the architecture, but can be implemented after the core information/knowledge path is working.

---

# 18. What We Deliberately Do NOT Finalize Yet

The architecture is intentionally incomplete in several implementation-level areas.

We have **not** finalized:

- physical storage technology,
- vector database vs relational vs graph vs hybrid storage,
- exact retrieval algorithm,
- embedding strategy,
- exact knowledge schema,
- exact confidence model,
- exact contradiction model,
- exact compression algorithm,
- exact promotion rules,
- exact staleness/decay policy,
- exact self-improvement trigger policy,
- exact event taxonomy,
- exact Agent Controller implementation,
- exact module/class structure.

These should be discovered/refined during implementation.

---

# 19. Why We Are Starting Implementation Now

We decided not to continue designing indefinitely.

The reasoning:

> The architecture is now sufficiently defined to establish boundaries, but implementation will expose constraints that cannot be predicted reliably through abstract design alone.

Therefore:

```text
Design hypothesis
      ↓
Implementation
      ↓
Testing
      ↓
Observed constraints
      ↓
Architecture refinement
      ↓
Next implementation slice
```

Prototype 3 should be developed iteratively.

---

# 20. Implementation Method

Every implementation step should follow:

```text
1. Inspect
       ↓
2. Design
       ↓
3. Implement
       ↓
4. Test
       ↓
5. Learn
       ↓
6. Refine architecture
```

Do not blindly implement the entire architecture upfront.

---

# 21. First Implementation Seam

After inspecting the current Terminal Agent branch:

`domain-expansion/knowledge-and-self-improvement-design`

the first implementation seam was identified around the **existing runtime-processing boundary**.

The current architecture already has a flow conceptually similar to:

```text
Tool Result
    ↓
normalize_result()
    ↓
artifact policy
    ↓
observation/formatting
    ↓
condense_memory()
    ↓
MemoryUpdateProposal
    ↓
mutate_state()
```

The current processing path already produces structured information such as:

- known facts,
- discovered resources,
- completed work,
- unresolved needs,
- evidence.

This makes it the natural seam for introducing the Prototype 3 information layer.

---

# 22. First Implementation Milestone

The first vertical slice should be:

## Prototype 3 — Information Foundation: Evidence + Provenance

Target flow:

```text
Tool Execution
      ↓
Runtime Processing
      ↓
Normalized Result
      ↓
Information Extraction
      ↓
Evidence Record
      ↓
Provenance
      ↓
Retained Information
      ↓
Later Retrieval
```

The first milestone should **not** attempt to implement the entire knowledge system.

---

# 23. Why Evidence Comes First

The original problem is information loss.

Before implementing sophisticated:

- knowledge graphs,
- embeddings,
- semantic retrieval,
- self-improvement,
- advanced context reconstruction,

we first need to establish:

> **A reliable representation of what the agent actually observed.**

If evidence cannot be retained reliably, every higher-level representation becomes questionable.

Therefore the first progression should be:

```text
Evidence
   ↓
Finding
   ↓
Understanding
   ↓
Knowledge
   ↓
Retrieval
   ↓
Context reconstruction
   ↓
Self-improvement
```

---

# 24. What Should Remain Untouched During the First Slice

The first implementation should avoid unnecessary changes to:

- runtime kernel,
- concurrent execution,
- TaskPlan,
- TaskExecutionCoordinator,
- ConcurrentTaskExecutor,
- workers,
- reconciliation,
- critics,
- core Prototype 2 execution behavior.

The goal is to add the information foundation **around the existing runtime**, not redesign it.

---

# 25. Current Architectural Picture

At the beginning of implementation, the working architecture is:

```text
                         TERMINAL AGENT
                              │
                              ▼
                       AGENT CONTROL
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   INVESTIGATION          KNOWLEDGE        SELF-IMPROVEMENT
      DOMAIN                DOMAIN              DOMAIN
          │                   │                   │
          ▼                   ▼                   ▼
      EXECUTION          INFORMATION          EXPERIENCE
       RUNTIME             PROCESSING          REFLECTION
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                       INFORMATION SYSTEM
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                RETRIEVAL           STORAGE
                    │
                    ▼
              CONTEXT BUILDER
                    │
                    ▼
              WORKING MEMORY
                    │
                    ▼
                   LLM
```

This diagram is the **current design hypothesis**, not a final implementation architecture.

---

# 26. Current Design Invariants

These should be treated as the strongest constraints during implementation.

1. **Terminal Agent is a subagent of CASO.**
2. **Prototype 2 runtime is considered healthy and should not be destabilized.**
3. **Working memory is not the authoritative knowledge store.**
4. **Information leaving working context should not automatically become lost.**
5. **Evidence must be retainable and traceable.**
6. **Derived understanding should preserve provenance.**
7. **Retrieval and context assembly are separate responsibilities.**
8. **Investigation is driven by information needs/questions.**
9. **Execution and cognition are separate domains.**
10. **Task knowledge and agent/self-improvement knowledge are separate concepts.**
11. **Self-improvement must not compromise active task execution.**
12. **Architecture should evolve based on implementation evidence.**
13. **Do not introduce complexity before the current vertical slice requires it.**
14. **Do not redesign the runtime merely to solve representation-layer problems.**

---

# 27. Open Questions to Resolve During Implementation

These are intentionally deferred.

## Information representation

- What exactly is an Evidence record?
- How should source/provenance be represented?
- How much raw content should be retained?
- How do we represent relationships?

## Processing

- When should raw evidence become a Finding?
- When should findings be synthesized into Understanding?
- Which transformations require an LLM?
- Which transformations should be deterministic?

## Storage

- What persistence mechanism is appropriate?
- What should be indexed?
- What should remain raw?
- How should task/project scope be represented?

## Retrieval

- Keyword?
- semantic?
- structural?
- graph-based?
- hybrid?

## Context

- How do we rank retrieved information?
- How do we budget context?
- How do we preserve important relationships while compressing?

## Knowledge evolution

- How do we detect contradiction?
- How do we handle stale codebase knowledge?
- How do we supersede older information?

## Self-improvement

- When should reflection happen?
- What counts as an improvement?
- How is an improvement evaluated?
- How is unsafe/unhelpful self-modification prevented?

These should be resolved when implementation provides enough concrete evidence to make the decision meaningful.

---

# 28. Prototype 3 Development Philosophy

The guiding philosophy is:

> **Build the smallest system that proves the information-retention problem is solved, then expand the information lifecycle based on real usage.**

We are not building a generic memory framework.

We are building an information/knowledge architecture specifically for the Terminal Agent's real workflow:

```text
Inspect
→ Understand
→ Retain
→ Retrieve
→ Reason
→ Investigate further
→ Synthesize
→ Produce rich output
```

---

# 29. Immediate Next Step

The next implementation action is:

> **Implement the Evidence + Provenance foundation at the existing runtime-processing boundary.**

Before writing code:

1. inspect the exact current `result_processing` implementation,
2. identify the minimal new information model,
3. define how it receives normalized runtime results,
4. implement the smallest vertical slice,
5. test retention and retrieval,
6. then update this document with what implementation taught us.

---

# 30. Design Change Log

This section should be updated throughout Prototype 3.

| Date | Change | Reason | Status |
|---|---|---|---|
| Initial | Prototype 3 introduced | Solve rich-information retention/readability problem | Accepted |
| Initial | Runtime preserved | Prototype 2 runtime considered healthy | Accepted |
| Initial | Working memory separated from knowledge | Avoid information loss due to context limitations | Accepted |
| Initial | Evidence introduced as first durable information boundary | Establish reliable source information before higher abstractions | Accepted |
| Initial | Self-improvement included as a separate domain | Incorporate useful Prime Agent concept without coupling it to task execution | Accepted |
| Initial | Implementation-first refinement strategy adopted | Avoid over-designing before concrete implementation constraints are known | Accepted |

---

# 31. Implementation Log

Use this section to record actual implementation discoveries.

## Iteration 1 — Evidence + Provenance

**Status:** Not started

### Goal

Create the first durable representation of acquired information without restructuring Prototype 2.

### Planned seam

```text
Runtime Processing
      ↓
Evidence Foundation
```

### Findings

_To be filled during implementation._

### Design changes

_To be filled during implementation._

### Tests

_To be filled during implementation._

---

# 32. Future Architecture Evolution

This document should evolve through implementation.

The expected progression is:

```text
Prototype 3
     │
     ▼
Evidence Foundation
     │
     ▼
Findings
     │
     ▼
Understanding
     │
     ▼
Knowledge
     │
     ▼
Retrieval
     │
     ▼
Context Reconstruction
     │
     ▼
Knowledge Refinement
     │
     ▼
Experience
     │
     ▼
Self-Improvement
```

The actual order may change if implementation reveals a better dependency structure.

---

# 33. Final Working Principle

The most important idea behind Prototype 3 is:

> **The model's context should be treated as a window into the Terminal Agent's information system, not as the Terminal Agent's entire memory.**

The Terminal Agent should be capable of:

```text
Observe
   ↓
Retain
   ↓
Understand
   ↓
Retrieve
   ↓
Reason
   ↓
Learn
   ↓
Improve
```

while keeping the existing execution runtime stable.

**Prototype 3 begins when we turn this principle into the first working Evidence + Provenance implementation.**
