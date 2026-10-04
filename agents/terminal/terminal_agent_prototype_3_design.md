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


---

# 34. Prototype 3 Current Status — Evidence Retention Complete

The first evidence-retention vertical slice has now been implemented and validated.

## 34.1 Evidence boundary

The runtime-processing boundary now produces structured `EvidenceRecord` objects from normalized tool results.

Evidence preserves:

- evidence identity,
- tool provenance,
- execution attempt,
- resource references,
- human-readable content,
- structured execution data.

The evidence path is deliberately downstream of runtime execution:

```
Tool Result
    ↓
Normalization
    ↓
Runtime Processing
    ↓
EvidenceRecord
    ↓
Evidence Store
```

The runtime itself remains unchanged.

## 34.2 Evidence storage

The first persistence seam is an `InMemoryEvidenceStore`.

The store is scoped by execution/thread identity so that evidence from one task/thread cannot leak into another.

The store supports:

- storing evidence,
- retrieving evidence by thread,
- retaining multiple executions in one thread,
- filtering within a thread boundary.

This is a prototype storage implementation, not the final persistence technology.

## 34.3 Boundary tests

The evidence foundation was validated with seven tests:

- evidence is emitted from tool-result processing,
- emitted evidence matches the normalized result,
- evidence generation does not mutate active memory,
- evidence is stored by thread,
- evidence is isolated between threads,
- multiple executions are retained in one thread,
- listing/filtering does not cross thread boundaries.

All seven tests pass.

This establishes the first important Prototype 3 invariant:

> **Information acquired during execution can leave active memory without being lost, while remaining traceable to its execution provenance.**

## 34.4 Important boundary

Evidence generation is currently deterministic.

The system should not ask an LLM merely to copy or persist raw execution results.

LLM-based processing belongs to higher-level transformations such as:

```
Evidence
   ↓
Finding
   ↓
Understanding
   ↓
Knowledge
```

This keeps the evidence layer reliable and auditable.

---

# 35. Retrieval Architecture — R1

With evidence retention established, the next architectural target is **R1: semantic retrieval**.

The retrieval problem is now:

> Given the current goal/information need, retrieve previously retained evidence that is semantically relevant enough to reconstruct useful working context.

The retrieval system should not read directly from active memory.

```
Information Need
      ↓
Retrieval Query
      ↓
Evidence Retrieval
      ↓
Candidate Evidence
      ↓
Relevance / Ranking
      ↓
Context Builder
      ↓
Working Memory
```

## 35.1 Retrieval remains separate from context assembly

Retrieval answers:

> Which retained evidence is potentially relevant?

Context assembly answers:

> Which retrieved evidence should actually enter the model context, in what order and representation?

These responsibilities remain separate.

---

# 36. R1 Retrieval Strategy

The current working design is a **semantic-first retrieval architecture with a deterministic lexical path available as a complementary signal**, rather than introducing an LLM decision-maker to choose retrieval modes.

The intended candidate flow is:

```
Query
  │
  ├───────────────┐
  ▼               ▼
Semantic Search   Lexical Search
  │               │
  └───────┬───────┘
          ▼
       RRF Fusion
          ▼
   Candidate Pool
          ▼
      Reranking
          ▼
   Retrieved Evidence
```

The important architectural decision is:

> **Retrieval strategy selection should not itself require an LLM call.**

An LLM deciding whether to use semantic or lexical retrieval would add latency, cost, and another failure surface to a component whose job should remain deterministic and measurable.

The system can combine retrieval signals directly and let ranking determine relevance.

---

# 37. Why Semantic Retrieval Is the Primary Signal

Terminal Agent questions are often expressed differently from the exact language contained in evidence.

For example:

```
Query:
"Where is runtime state reconciled?"

Evidence:
"Execution state is merged during the reconciliation stage..."
```

A semantic representation can connect these even when exact lexical overlap is limited.

Semantic retrieval is therefore particularly useful for:

- conceptual questions,
- architectural understanding,
- paraphrased questions,
- relationships expressed in different language,
- finding evidence that supports a broader investigation goal.

However, semantic similarity alone should not be assumed to be sufficient for all codebase information.

Exact identifiers, filenames, symbols, error messages, and command output often benefit from lexical matching.

Therefore R1 should measure both signals rather than prematurely committing the entire system to a single retrieval mechanism.

---

# 38. Candidate R1 Technology

The current technology candidates are:

## Vector database

**LanceDB** is the current prototype candidate.

Reasons:

- purpose-built vector retrieval,
- metadata filtering,
- support for payloads alongside vectors,
- straightforward local/self-hosted deployment,
- suitable separation between evidence storage and retrieval index.

The final storage technology remains replaceable.

## Embeddings

**Jina Embeddings v4** is the current embedding candidate for experimentation.

The embedding provider must remain behind an interface so the retrieval architecture does not become coupled to one model.

Conceptually:

```
EmbeddingProvider
       │
       ├── Jina implementation
       └── future implementation
```

The embedding model should therefore be treated as an implementation choice, not an architectural invariant.

---

# 39. Evidence Store vs Retrieval Index

A critical distinction:

```
Evidence Store
    ↓
Source of truth

Retrieval Index
    ↓
Derived searchable representation
```

The vector index must never become the authoritative copy of evidence.

If an index is rebuilt, changed, or deleted, the underlying evidence must remain recoverable from the evidence store.

Conceptually:

```
                 Evidence Store
                  /           \
                 /             \
                ▼               ▼
        Semantic Index     Lexical Index
                \               /
                 \             /
                  ▼           ▼
                    Retrieval
```

This preserves storage/retrieval separation.

---

# 40. Evidence Metadata for Retrieval

R1 retrieval should not rely only on the embedding.

Evidence should expose metadata that can constrain or improve retrieval, including where available:

- thread/task scope,
- provenance/tool name,
- execution attempt,
- resource references,
- evidence type,
- creation timestamp,
- content,
- structured data,
- source identity.

Metadata enables deterministic filtering before or alongside semantic ranking.

Examples:

```
thread_id = current_thread
resource = agents/terminal/...
tool = run_terminal
```

This prevents semantically similar evidence from unrelated tasks from entering the candidate pool.

---

# 41. R1 Retrieval Contract

The retrieval boundary should be expressed as a contract rather than coupled directly to Qdrant or another backend.

Conceptually:

```text
retrieve(
    query,
    scope,
    filters,
    limit
) -> RetrievalResult
```

The contract should allow the caller to specify:

- natural-language query,
- retrieval scope,
- metadata filters,
- candidate limit.

The result should return evidence references plus retrieval metadata such as:

- evidence ID,
- relevance score,
- retrieval source,
- rank,
- provenance.

The contract should not expose vector-database-specific concepts to the rest of the Terminal Agent.

---

# 42. R1 Retrieval Trigger

Retrieval should be triggered by an **information need**, not by every tool call.

The intended control flow is:

```
Agent reasoning
      ↓
Information need detected
      ↓
Retrieval request
      ↓
Relevant evidence
      ↓
Context assembly
```

A tool execution may produce new evidence, but producing evidence does not automatically mean the system must perform another retrieval operation.

This avoids unnecessary retrieval churn.

Retrieval can be triggered when:

- the current context is insufficient,
- the agent needs to recall an earlier discovery,
- the agent is about to investigate something already likely to have retained evidence,
- the context builder needs supporting evidence,
- a synthesis step requires historical evidence.

---

# 43. Retrieval Quality Requirements

R1 should be evaluated experimentally rather than assumed to work because a vector database is present.

The initial evaluation should measure:

1. **Recall** — did relevant evidence appear?
2. **Precision@K** — how much of the returned top-K evidence is relevant?
3. **Ranking quality** — does the most useful evidence appear early?
4. **Scope isolation** — does retrieval stay within the correct thread/task boundary?
5. **Latency** — is retrieval cheap enough for iterative agent reasoning?
6. **Context usefulness** — does retrieved evidence actually improve downstream reasoning?

The final metric is especially important.

A retrieval system that returns semantically similar text but does not improve the agent's ability to answer the actual task is not solving the Prototype 3 problem.

---

# 44. R1 Does Not Yet Include

The following remain intentionally deferred:

- graph retrieval,
- multi-hop retrieval,
- sophisticated knowledge-graph construction,
- learned retrieval policies,
- query planning by LLM,
- automatic retrieval-mode selection by LLM,
- long-term generalized agent memory,
- advanced self-improvement,
- automatic knowledge promotion,
- complex contradiction resolution.

These can be added only when the simpler retrieval boundary demonstrates a real need for them.

---

# 45. Planned Retrieval Progression

The current Prototype 3 roadmap is:

```
P3-1  Evidence + Provenance          COMPLETE
          ↓
P3-2  R1 Retrieval Foundation        NEXT
          ↓
P3-3  Reranking / relevance quality
          ↓
P3-4  Context quality + diversity
          ↓
P3-5  Multi-hop / relationship-aware retrieval
          ↓
P3-6  Knowledge synthesis
          ↓
P3-7  Self-improvement
```

This is a working roadmap, not a rigid commitment.

Each stage should be validated before the next layer is introduced.

---

# 46. Implementation Principle Added After Evidence Work

A new implementation principle emerged from the first vertical slice:

> **Do not make the evidence layer intelligent before making it reliable.**

The system should first preserve what happened accurately.

Only after reliable retention exists should the system introduce increasingly intelligent transformations.

```
Reliable evidence
      ↓
Reliable retrieval
      ↓
Useful synthesis
      ↓
Useful self-improvement
```

This ordering reduces the risk of building sophisticated reasoning on top of corrupted, incomplete, or untraceable information.

---

# 47. Updated Immediate Next Step

The next implementation action is now:

> **Implement R1 retrieval against the retained EvidenceRecord boundary without changing the existing runtime architecture.**

The implementation should proceed in this order:

1. define the retrieval contract,
2. define the embedding/index seam,
3. create the first retrieval index,
4. index retained evidence,
5. implement semantic candidate retrieval,
6. add lexical/RRF fusion if the current design validates the need,
7. add ranking/reranking only after candidate retrieval is measurable,
8. test thread/scope isolation,
9. evaluate retrieval quality,
10. update this document with observed results.

The retrieval implementation must remain replaceable and must not make the evidence store dependent on the chosen search technology.

---

# 48. Current Prototype 3 Status

| Component | Status |
|---|---|
| Architecture principles | Complete |
| Architectural requirements/invariants | Complete |
| Evidence model | Complete |
| Evidence provenance | Complete |
| Runtime-processing integration | Complete |
| In-memory evidence store | Complete |
| Evidence boundary tests | Complete — 7/7 |
| Retrieval contracts | Established |
| R1 semantic retrieval design | Established |
| Retrieval backend | Candidate: Qdrant |
| Embedding model | Candidate: Jina Embeddings v4 |
| RRF/lexical fusion | Planned for R1 evaluation |
| Reranking | Later |
| Context reconstruction | Later |
| Knowledge synthesis | Later |
| Self-improvement | Later |

---

# 49. Design Change Log — Latest

| Date | Change | Reason | Status |
|---|---|---|---|
| Current iteration | Evidence retention implemented | Establish durable information boundary | Complete |
| Current iteration | In-memory evidence store added | Establish thread-scoped retention seam | Complete |
| Current iteration | Seven boundary tests passing | Validate evidence/store invariants | Complete |
| Current iteration | Evidence generation kept deterministic | Preserve auditable source information | Accepted |
| Current iteration | Retrieval separated from evidence storage | Keep source of truth independent from search infrastructure | Accepted |
| Current iteration | R1 semantic retrieval defined | Enable retrieval of retained information outside active memory | Accepted |
| Current iteration | LLM retrieval-mode selection rejected | Avoid unnecessary latency/cost and preserve deterministic retrieval behavior | Accepted |
| Current iteration | Qdrant selected as current vector-store candidate | Prototype semantic retrieval infrastructure | Candidate |
| Current iteration | Jina Embeddings v4 selected as current embedding candidate | Prototype semantic representation | Candidate |
| Current iteration | RRF fusion retained as an evaluation path | Combine semantic and lexical signals without an LLM router | Planned |

---

# 50. Implementation Log — Iteration 1

## Evidence + Provenance

**Status:** Complete

### Result

The runtime-processing boundary now emits evidence independently of active-memory mutation.

Evidence can be retained by thread and retrieved without requiring the evidence to remain in active memory.

### Tests

**7/7 passing.**

### Architectural conclusion

The evidence boundary is sufficiently stable to begin retrieval work.

---

## Iteration 2 — R1 Retrieval

**Status:** Next

### Goal

Retrieve previously retained evidence using the current information need and construct a candidate set for later context assembly.

### Findings

_To be filled during implementation._

### Design changes

_To be filled during implementation._

### Tests

_To be filled during implementation._



---

# 51. Retrieval Phases — R1 to R5

The retrieval architecture is intentionally being developed in phases. Each phase should prove a specific capability before the next layer is introduced.

## R1 — Retrieval Foundation

**Goal:** Establish reliable retrieval over retained Evidence.

Scope:

- Search Document representation.
- Embedding provider abstraction.
- Dense semantic retrieval.
- Lexical/BM25 retrieval.
- Thread/scope filtering.
- Candidate generation.
- RRF candidate fusion.

Target flow:

```text
EvidenceStore
     ↓
Search Representation
     ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Dense           BM25
 │               │
 └───────┬───────┘
         ▼
        RRF
         ▼
Candidate Evidence
```

**R1 success condition:**

The Terminal Agent can retrieve relevant retained Evidence for realistic information needs without requiring an LLM to choose the retrieval mechanism.

---

## R2 — Precision / Reranking

**Goal:** Improve ordering and precision after broad candidate generation.

Scope:

- Reranker interface.
- Candidate scoring.
- Top-K selection.
- Retrieval evaluation against realistic Terminal Agent questions.

Target flow:

```text
R1 Candidate Pool
       ↓
    Reranker
       ↓
 Ranked Evidence
       ↓
      Top-K
```

The reranker operates only on the relatively small R1 candidate set. It is not responsible for searching the entire Evidence corpus.

**R2 success condition:**

The most useful evidence consistently appears near the top of the retrieved set, with measurable improvement over the R1 ranking.

---

## R3 — Context Quality / Diversity

**Goal:** Turn retrieved evidence into a compact, useful reasoning context.

Scope:

- duplicate reduction,
- evidence diversity,
- context budgeting,
- ordering,
- compression where justified,
- preservation of provenance/resource references.

Potential technique:

- MMR or another diversity-selection mechanism.

Target flow:

```text
Ranked Evidence
       ↓
Diversity / Deduplication
       ↓
Context Budgeting
       ↓
Context Builder
       ↓
Working Context
```

**R3 success condition:**

The context contains complementary evidence rather than many near-duplicate results, while staying within the intended context budget.

---

## R4 — Multi-Hop / Relationship-Aware Retrieval

**Goal:** Support repository questions that cannot be answered from a single retrieval pass.

Scope:

- iterative information needs,
- query reformulation,
- relationship-aware traversal,
- follow-up retrieval,
- dependency exploration,
- evidence chains.

Target flow:

```text
Information Need
       ↓
Retrieve
       ↓
Evidence
       ↓
Reason
       ↓
Unresolved dependency?
   ├── No → Continue
   └── Yes
          ↓
     New retrieval query
          ↓
       Retrieve
          ↓
         ...
```

Typical Terminal Agent example:

```text
"What is responsible for task execution?"

        ↓

retrieve executor evidence

        ↓

discover coordinator dependency

        ↓

retrieve coordinator evidence

        ↓

discover reconciliation

        ↓

retrieve reconciliation evidence

        ↓

build a complete understanding
```

**R4 success condition:**

The agent can follow multi-step evidence chains and accumulate enough related evidence to answer repository-level questions that a single retrieval pass cannot resolve.

---

## R5 — Retrieval Self-Improvement

**Goal:** Use Terminal Agent experience to improve retrieval quality over time.

Scope:

- retrieval trajectory capture,
- successful/failed retrieval analysis,
- missed-evidence detection,
- query reformulation analysis,
- ranking feedback,
- retrieval evaluation history,
- candidate training/evaluation datasets.

Potential signal:

```text
Goal
 ↓
Queries issued
 ↓
Evidence retrieved
 ↓
Files/resources inspected
 ↓
Reasoning
 ↓
Successful conclusion
```

This can be analyzed to determine:

- which evidence should have been retrieved earlier,
- which retrieval results were unnecessary,
- where semantic ranking failed,
- where lexical retrieval was important,
- which query formulations work well,
- where the agent repeatedly performs redundant investigation.

The long-term architecture is:

```text
Agent Trajectory
      ↓
Retrieval Feedback
      ↓
Evaluation
      ↓
Retrieval Improvement
      ↓
Future Retrieval
```

R5 is intentionally later than the base retrieval pipeline. We should not attempt retrieval-model self-training before R1–R4 are measurable.

**R5 success condition:**

Retrieval quality can improve from accumulated Terminal Agent experience without making self-improvement part of the critical execution path.

---

# 52. Retrieval Phase Dependency

The intended dependency is:

```text
R1 Foundation
      ↓
R2 Reranking
      ↓
R3 Context Quality
      ↓
R4 Multi-Hop
      ↓
R5 Self-Improvement
```

A later phase may be pulled forward only when implementation evidence shows a strong dependency.

The phases are **capability boundaries**, not arbitrary milestones.

---

# 53. Retrieval Technology Stack — Current Direction

The current experimental stack is:

```text
EvidenceStore
      ↓
Search Document Builder
      ↓
Embedding Provider
      ↓
Dense Index

EvidenceStore
      ↓
Search Document Builder
      ↓
BM25 / Sparse Index

Dense + Sparse
      ↓
RRF
      ↓
Reranker
      ↓
Diversity / Context Builder
```

Current technology candidates:

| Capability | Current candidate | Notes |
|---|---|---|
| Dense embeddings | Jina Embeddings v4 | Candidate only; hidden behind provider interface |
| Dense/vector index | Qdrant | Leading candidate; replaceable |
| Sparse retrieval | BM25 | Strong exact/code identifier baseline |
| Candidate fusion | RRF | Initial fusion mechanism |
| Reranking | Dedicated reranker | To be selected/evaluated in R2 |
| Diversity | MMR | To be introduced only if evaluation justifies it |
| Multi-hop | Agent-driven iterative retrieval | R4 |
| Retrieval improvement | Trajectory-based feedback | R5 |

These technology choices remain subject to evaluation.

---

# 54. Retrieval Design Invariants

The following retrieval-specific invariants are now added:

1. **EvidenceStore remains the authoritative source of retained information.**
2. **Dense and sparse retrieval are complementary signals rather than mutually exclusive modes.**
3. **No LLM call is required merely to select dense versus sparse retrieval.**
4. **Retrieval indexes are derived state and must be rebuildable from retained Evidence.**
5. **Search representations may differ from authoritative EvidenceRecords.**
6. **Retrieval must remain thread/scope aware.**
7. **Retrieval returns Evidence; Context Builder decides what enters model context.**
8. **Reranking operates on a bounded candidate set rather than the entire Evidence corpus.**
9. **Multi-hop retrieval is an iterative reasoning capability, not a requirement for the first retrieval implementation.**
10. **Retrieval self-improvement must remain outside the critical execution path.**
11. **Advanced retrieval techniques must be justified by measured failure modes.**


---

# 55. R1.1 — Retrieval Contract & Search Representation Design

**Status:** Locked design; implementation next.

R1.1 establishes the stable interfaces between retained Evidence and future retrieval implementations. It intentionally stops before introducing Qdrant, an embedding model, BM25 implementation, RRF, reranking, runtime integration, or retrieval triggering.

The purpose is to make the retrieval subsystem replaceable and testable before infrastructure is introduced.

## 55.1 R1.1 boundary

```text
EvidenceRecord
      ↓
SearchDocumentBuilder
      ↓
SearchDocument
      ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Dense Retrieval  Lexical Retrieval
```

R1.1 defines the contracts and representations represented by the boxes. Later subphases implement the arrows.

## 55.2 Existing retrieval query

The existing `EvidenceRetrievalQuery` is retained as the public information-need contract:

```text
query
resource_refs
tool_name
limit
```

The query expresses:

- the semantic information need,
- optional deterministic resource constraints,
- optional tool constraint,
- desired result limit.

It must not expose backend-specific concepts such as vector dimensions, Qdrant collections, BM25 parameters, or reranker configuration.

## 55.3 RetrievedEvidence

Retrieval should return ranked evidence rather than bare EvidenceRecord objects.

Conceptually:

```text
RetrievedEvidence
├── evidence
├── score
├── rank
└── source
```

The `source` identifies how the result was produced, for example:

- `semantic`
- `lexical`
- `rrf`
- later `reranked`

This makes the retrieval system observable and gives R1 measurable ranking information.

## 55.4 EvidenceRetrievalResult

The public retrieval result becomes:

```text
EvidenceRetrievalResult
├── query
├── results[]
└── total_candidates
```

The result therefore describes both the original information request and its ranked retrieved evidence.

## 55.5 SearchDocument

`SearchDocument` is derived searchable state, not authoritative Evidence.

Conceptually:

```text
SearchDocument
├── document_id
├── evidence_id
├── text
├── thread_id
├── resource_refs
├── tool_name
└── metadata
```

The `thread_id` is included in the derived search representation so retrieval indexes can enforce the same isolation boundary as the EvidenceStore.

EvidenceRecord itself does not need to duplicate this ownership information.

## 55.6 SearchDocumentBuilder

A dedicated builder converts an authoritative EvidenceRecord into a retrieval representation:

```text
EvidenceRecord
      ↓
SearchDocumentBuilder
      ↓
SearchDocument
```

The builder is responsible for producing contextualized searchable text and retrieval metadata.

It does **not**:

- generate embeddings,
- write to an index,
- perform retrieval,
- mutate the EvidenceRecord.

This keeps representation, indexing, and retrieval separate.

## 55.7 EmbeddingProvider

R1.1 defines a replaceable embedding boundary:

```text
EmbeddingProvider
      ↓
text(s) → vector(s)
```

The interface must not expose a specific embedding vendor or model to the rest of Terminal Agent.

The current experimental candidate remains Jina Embeddings v4, but that is a technology choice rather than an architectural invariant.

## 55.8 DenseIndex

The dense index owns vector storage/search:

```text
SearchDocument
      ↓
EmbeddingProvider
      ↓
vector
      ↓
DenseIndex
```

Its interface should support:

- indexing/upserting searchable documents with vectors,
- thread-scoped vector search,
- bounded candidate retrieval.

The rest of Terminal Agent must not depend directly on Qdrant or another vector engine.

## 55.9 LexicalIndex

The lexical index is the complementary exact/lexical retrieval boundary.

The intended first implementation is BM25.

It should support:

- indexing SearchDocuments,
- thread-scoped lexical search,
- bounded candidate retrieval.

The lexical implementation remains replaceable.

## 55.10 EvidenceRetriever

The public retrieval abstraction hides all backend details:

```text
EvidenceRetrievalQuery
        ↓
EvidenceRetriever
        ↓
EvidenceRetrievalResult
```

The caller should not need to know whether retrieval used:

- Qdrant,
- FAISS,
- BM25,
- Jina,
- another embedding model,
- or another future implementation.

## 55.11 R1.1 dependency structure

```text
                    EvidenceStore
                         │
                         ▼
               SearchDocumentBuilder
                         │
                         ▼
                  SearchDocument
                    /         \
                   /           \
                  ▼             ▼
          EmbeddingProvider   LexicalIndex
                  │
                  ▼
              DenseIndex
                    \         /
                     \       /
                      ▼     ▼
                    Retrieval
```

R1.1 defines this dependency structure but does not yet implement candidate generation.

## 55.12 R1.1 invariants

1. EvidenceRecord remains the source of truth.
2. SearchDocument is derived state.
3. SearchDocument is retrieval-oriented and must not replace EvidenceRecord.
4. Retrieval never mutates Evidence.
5. Retrieval is thread/scope aware.
6. Query models must remain backend-agnostic.
7. Retrieval results expose rank, score, and source.
8. Embedding providers are replaceable.
9. Dense and lexical index implementations are replaceable.
10. Artifact retrieval remains separate from Evidence retrieval.
11. Context Builder decides what retrieved evidence enters model context.
12. No runtime architecture changes are required for R1.1.

---

# 56. R1.1 → R1.7 Implementation Subphases

R1 is divided into seven implementation subphases. Each subphase has a concrete capability boundary and should be validated before progressing.

## R1.1 — Contracts & Search Representation

**Goal:** Establish the stable retrieval interfaces.

Scope:

- `EvidenceRetrievalQuery`
- `RetrievedEvidence`
- `EvidenceRetrievalResult`
- `SearchDocument`
- `SearchDocumentBuilder`
- `EmbeddingProvider`
- `DenseIndex`
- `LexicalIndex`
- `EvidenceRetriever`

No retrieval infrastructure is introduced here.

**Exit condition:**

All contracts can be instantiated/tested independently and contain no backend-specific dependencies.

---

## R1.2 — Search Representation + Embedding Seam

**Goal:** Turn retained Evidence into an indexable semantic representation.

Flow:

```text
EvidenceRecord
      ↓
SearchDocumentBuilder
      ↓
SearchDocument
      ↓
EmbeddingProvider
      ↓
Vector
```

Scope:

- contextual searchable text generation,
- metadata construction,
- embedding provider implementation seam,
- deterministic handling of empty/invalid text,
- vector shape validation.

Initial technology experiment:

- Jina Embeddings v4 candidate.

**Exit condition:**

A retained EvidenceRecord can deterministically produce a SearchDocument and a valid embedding through the abstraction.

---

## R1.3 — Dense Semantic Retrieval

**Goal:** Prove semantic retrieval independently.

Flow:

```text
RetrievalQuery
      ↓
EmbeddingProvider
      ↓
Query Vector
      ↓
DenseIndex
      ↓
Semantic Candidates
```

Scope:

- dense index implementation,
- indexing SearchDocuments,
- query embedding,
- similarity search,
- thread-scoped filtering,
- score/rank mapping.

Initial technology candidate:

- Qdrant,
- with a local/in-memory alternative available for isolated tests where useful.

**Exit condition:**

Relevant Evidence can be recovered by semantic similarity within the correct thread/scope.

---

## R1.4 — Lexical / BM25 Retrieval

**Goal:** Add exact lexical retrieval for identifiers, filenames, symbols, errors, and other terms where semantic search can be weak.

Flow:

```text
RetrievalQuery
      ↓
LexicalIndex / BM25
      ↓
Lexical Candidates
```

Scope:

- BM25 index,
- SearchDocument indexing,
- thread/scope filtering,
- lexical score/rank mapping.

**Exit condition:**

Exact and lexical-heavy Terminal Agent queries can retrieve relevant Evidence reliably.

---

## R1.5 — Candidate Fusion / RRF

**Goal:** combine dense and lexical candidate sets without an LLM routing decision.

Flow:

```text
Dense Candidates
       +
Lexical Candidates
       ↓
RRF
       ↓
Unified Candidate Ranking
```

Scope:

- Reciprocal Rank Fusion,
- duplicate evidence merging,
- deterministic tie handling,
- unified `RetrievedEvidence` representation.

The retriever should run both candidate generators rather than asking an LLM which one to use.

**Exit condition:**

Hybrid retrieval improves coverage over either signal alone on the initial evaluation set.

---

## R1.6 — Retrieval Evaluation & Failure Analysis

**Goal:** make retrieval quality measurable before adding R2 reranking.

Scope:

- realistic Terminal Agent retrieval questions,
- labeled relevant Evidence,
- Recall@K,
- Precision@K,
- ranking quality,
- scope-isolation checks,
- latency measurements,
- redundant-result analysis,
- failure classification.

Important principle:

> Do not add reranking, query rewriting, MMR, or multi-hop logic merely because those techniques exist. Add them only when R1 measurements demonstrate a concrete failure mode.

**Exit condition:**

We have a reproducible R1 evaluation set and can explain where the retrieval system succeeds and fails.

---

## R1.7 — R1 Integration Boundary

**Goal:** expose the validated retrieval capability to the Terminal Agent without redesigning the existing execution runtime.

Flow:

```text
Agent / Information Need
          ↓
EvidenceRetrievalQuery
          ↓
EvidenceRetriever
          ↓
EvidenceRetrievalResult
```

Scope:

- dependency wiring,
- retrieval service lifetime,
- thread/scope propagation,
- retrieval observability,
- narrow integration seam for future Context Builder use.

R1.7 should **not** implement the final retrieval trigger policy or Context Builder.

Those remain higher-level responsibilities.

**Exit condition:**

Terminal Agent can invoke the retrieval subsystem through the stable contract and receive ranked, thread-scoped evidence without knowing the search backend.

---

# 57. R1 Subphase Dependency

```text
R1.1 Contracts
      ↓
R1.2 Search Representation
      ↓
R1.3 Dense Retrieval
      ↓
R1.4 Lexical Retrieval
      ↓
R1.5 RRF Fusion
      ↓
R1.6 Evaluation
      ↓
R1.7 Integration
```

R1.6 is intentionally before R2 because the system should measure the baseline before introducing a more expensive reranking stage.

---

# 58. R1 Technology Boundary

The following are **current implementation candidates**, not permanent architectural decisions:

| Layer | Current candidate | Architectural rule |
|---|---|---|
| Embedding model | Jina Embeddings v4 | Hidden behind EmbeddingProvider |
| Dense index | Qdrant | Hidden behind DenseIndex |
| Lexical retrieval | BM25 | Hidden behind LexicalIndex |
| Fusion | RRF | Implemented independently of storage |
| Reranking | Deferred to R2 | Must not leak into R1 contracts |
| Diversity/MMR | Deferred to R3 | Must be justified by evaluation |
| Multi-hop | Deferred to R4 | Higher-level iterative retrieval |
| Self-improvement | Deferred to R5 | Outside critical retrieval path |

---

# 59. R1 Completion Criteria

R1 is complete only when all of the following are demonstrated:

1. Retained Evidence can be transformed into searchable representation.
2. Semantic retrieval works within thread/scope boundaries.
3. Lexical retrieval works for exact/code-oriented queries.
4. Dense and lexical candidates can be fused deterministically.
5. Retrieval results expose useful ranking metadata.
6. Retrieval quality has a reproducible evaluation baseline.
7. Terminal Agent can call retrieval through the public contract.
8. No backend-specific concepts leak into Terminal Agent's higher-level control logic.
9. The existing Prototype 2 execution architecture remains unchanged.
10. Retrieval is ready to become an input to the later Context Builder.

---

# 60. R1.1 Implementation Checklist

- [ ] Add `RetrievedEvidence`
- [ ] Update `EvidenceRetrievalResult`
- [ ] Add `SearchDocument`
- [ ] Add `SearchDocumentBuilder`
- [ ] Add `EmbeddingProvider` protocol
- [ ] Add `DenseIndex` protocol
- [ ] Add `LexicalIndex` protocol
- [ ] Add `EvidenceRetriever` protocol
- [ ] Keep EvidenceStore unchanged
- [ ] Keep ArtifactRetriever unchanged
- [ ] Add focused contract/model tests
- [ ] Update this design record with implementation findings

---

# 61. Design Status

**R1.1 is locked for implementation.**

The next code change should implement only the R1.1 contracts and search representation models.

No Qdrant setup, embedding model integration, BM25 implementation, RRF, runtime integration, or retrieval trigger should be introduced until the R1.1 boundary is validated.


---

# 62. R1.2-A — Semantic Projection Locked

**Status:** Locked.

R1.2-A establishes the semantic projection from authoritative Evidence into retrieval-oriented SearchDocuments.

## 62.1 Core distinction

```
EvidenceRecord
    = authoritative observed information

SearchDocument
    = derived retrieval unit

RetrievedEvidence
    = ranked retrieval result
```

`RetrievedEvidence` must never be embedded because `score`, `rank`, and `source` describe retrieval state rather than the underlying information.

## 62.2 Semantic projection

The projection is deterministic for the initial Prototype 3 implementation:

```
EvidenceRecord
      ↓
Semantic Projection
      ↓
Search text + retrieval metadata
      ↓
SearchDocument
```

The initial searchable text should preserve:

- primary evidence content,
- resource/file/path identifiers verbatim,
- relevant structured execution information,
- useful terminal output/error information.

The following remain metadata rather than primary semantic content:

- evidence ID,
- thread ID,
- execution bookkeeping,
- provenance fields used only for filtering/audit,
- artifact references where they do not contribute semantic meaning.

## 62.3 Large evidence and chunking

An EvidenceRecord is the authoritative retention unit, but it is not required to be a single retrieval unit.

```
Small/coherent EvidenceRecord
        ↓
   one SearchDocument

Large/multi-topic EvidenceRecord
        ↓
 multiple SearchDocuments
```

Chunking exists to avoid semantic dilution and to allow retrieval to target a relevant portion of large terminal/file/tool output.

Chunking must **not** destroy the original evidence. The complete EvidenceRecord remains in EvidenceStore.

Each derived chunk retains:

- original `evidence_id`,
- stable `chunk_id`,
- `thread_id`,
- resource references,
- provenance metadata.

Chunking thresholds and overlap strategy remain implementation/evaluation decisions rather than arbitrary fixed values.

## 62.4 SearchDocument identity

Derived search documents must have deterministic identity so re-indexing remains idempotent.

Conceptually:

```
document_id = stable(evidence_id, chunk_id)
```

The exact identifier/hash implementation is an R1.2 implementation detail.

## 62.5 Search representation rule

The initial representation uses **one canonical searchable text** for both dense and lexical retrieval.

We do not create separate semantic and lexical projections yet.

R1.6 evaluation may justify splitting them later.

## 62.6 LLM contextualization decision

The initial SearchDocument projection is deterministic.

No LLM is required to summarize or rewrite evidence before indexing.

This preserves:

- reproducibility,
- auditability,
- exact identifiers,
- original evidence fidelity.

An explicit semantic-enrichment stage may be added later only if evaluation demonstrates that deterministic projection is insufficient.

## 62.7 R1.2-A invariants

1. EvidenceRecord remains authoritative.
2. SearchDocument is derived and rebuildable.
3. RetrievedEvidence is never an embedding source.
4. Exact identifiers, paths, filenames, symbols, commands, and error strings are preserved.
5. Metadata is not blindly serialized into semantic text.
6. Large Evidence may produce multiple SearchDocuments.
7. All derived chunks retain the original evidence identity.
8. SearchDocument identity is deterministic.
9. Initial projection is deterministic and does not require an LLM.
10. Complete source Evidence remains retained independently of search chunks.

---

# 63. R1.2-B — Qwen3 Embedding Provider Design

**Status:** Provider selected; implementation design locked.

## 63.1 Selected provider

The initial free/local embedding model for Terminal Agent Prototype 3 is:

```
Qwen/Qwen3-Embedding-0.6B
```

The model is selected as an initial implementation candidate because it is open-weight, Apache-2.0 licensed, designed for retrieval workloads including code-oriented use cases, supports long inputs, and can be run locally without per-request API cost.

This is a technology choice, not a permanent architecture dependency.

## 63.2 Provider abstraction

The provider-specific implementation remains behind the provider contract.

The rest of Terminal Agent interacts with:

```
EmbeddingProvider
      ↓
embed_documents()
embed_queries()
```

rather than directly importing Qwen classes.

## 63.3 Query/document asymmetry

Qwen3 retrieval usage distinguishes document encoding from query encoding.

Therefore the provider contract should expose two explicit operations:

```
embed_documents(texts)
embed_queries(texts)
```

Documents are encoded as searchable document text.

Queries may use a configurable retrieval instruction/prefix appropriate to the embedding model.

This model-specific behavior remains inside `Qwen3EmbeddingProvider`.

## 63.4 Initial provider configuration

The initial configuration is:

| Property | Initial value |
|---|---|
| Model | `Qwen/Qwen3-Embedding-0.6B` |
| Default dimension | 1024 |
| Maximum input context | 32K tokens |
| Execution | Local |
| Device | Configurable |
| Batch size | Configurable |
| Normalization | Configurable |
| Query instruction | Configurable |

The architecture must not hard-code 1024 dimensions as a global system invariant because the model supports configurable output dimensions.

## 63.5 Batch-first API

Embedding APIs operate on lists:

```
embed_documents(list[str])
embed_queries(list[str])
```

This supports efficient indexing and avoids forcing the indexing layer into one-request-per-document operation.

## 63.6 Validation

The provider must validate:

- empty batch behavior,
- non-empty text requirements for individual documents,
- document/vector count alignment,
- consistent vector dimensions within a batch,
- invalid provider responses,
- configured dimension compatibility.

No silent truncation or vector/document mismatch is acceptable.

## 63.7 Dependency choice

The existing Terminal Agent environment already includes SentenceTransformers and the transformer stack.

The first provider implementation may therefore use SentenceTransformers as the execution wrapper while keeping the public architecture provider-agnostic.

## 63.8 R1.2-B invariants

1. Qwen3 is an implementation choice, not a system-wide dependency.
2. Document and query embedding paths remain distinct.
3. EmbeddingProvider exposes no Qwen-specific object types.
4. Batch processing is the default API shape.
5. Vector count must match input count.
6. Vector dimensionality must be consistent for an embedding-provider instance.
7. Provider configuration owns model/device/batch/normalization/instruction details.
8. SearchDocument and EvidenceRecord remain independent of the embedding implementation.
9. No vector database is introduced in R1.2-B.

---

# 64. R1.2 Implementation Boundary

R1.2 is divided into:

```
R1.2-A
Semantic Projection
        ↓
R1.2-B
Embedding Provider
        ↓
R1.3
Dense Index / Semantic Retrieval
```

The intended R1.2 flow is therefore:

```
EvidenceRecord
      ↓
SearchDocumentBuilder
      ↓
SearchDocument
      ↓
Qwen3EmbeddingProvider
      ↓
Embedded representation
```

R1.2 does not search the index.

R1.2 does not perform BM25 retrieval.

R1.2 does not perform RRF.

R1.2 does not perform reranking.

R1.2 does not modify the runtime graph.

---

# 65. R1.2-B Technology Decision Notes

The provider comparison considered:

- Qwen3-Embedding-0.6B,
- Qwen3-Embedding-4B,
- Qwen3-Embedding-8B,
- BGE-M3,
- Nomic Embed v1.5,
- Jina Embeddings v4.

The current choice is Qwen3-Embedding-0.6B because Prototype 3 prioritizes:

- free/local operation,
- manageable resource requirements,
- code-oriented retrieval suitability,
- long input support,
- replaceable provider architecture,
- fast experimental iteration.

Higher-capacity models remain candidates for later evaluation if R1.6 demonstrates a quality gap.

---

# 66. Immediate R1.2 Implementation Checklist

## R1.2-A

- [ ] Implement deterministic SearchDocumentBuilder
- [ ] Preserve paths/symbols/identifiers
- [ ] Project relevant structured execution data
- [ ] Define large-evidence handling boundary
- [ ] Define stable document/chunk IDs
- [ ] Add projection tests

## R1.2-B

- [ ] Refine EmbeddingProvider to separate document/query embedding
- [ ] Implement Qwen3EmbeddingProvider
- [ ] Add provider configuration
- [ ] Add batch embedding
- [ ] Validate vector count
- [ ] Validate vector dimensions
- [ ] Handle empty input
- [ ] Add provider tests
- [ ] Keep index/backend integration out of R1.2

## R1.2 exit condition

A retained EvidenceRecord can be deterministically converted into one or more SearchDocuments and those documents can be embedded locally through the selected Qwen3 provider with validated vector output.

---

# 67. R1.2 Implementation Progress

**Status:** Implementation complete at the unit-test boundary; real-provider smoke validation pending.

The R1.2 implementation now contains:

- deterministic `SearchDocument` projection,
- stable document identity,
- `chunk_id` support in the search representation,
- provider-agnostic `EmbeddingProvider` with separate document/query paths,
- `EmbeddedDocument`,
- `Qwen3EmbeddingConfig`,
- `Qwen3EmbeddingProvider`,
- vector count validation,
- vector dimension validation,
- batch embedding,
- empty-input handling,
- provider error handling.

The focused R1.2 tests pass, including projection and provider-contract tests.

However, the unit tests inject a fake embedding model. Therefore the R1.2 exit condition is not yet considered fully demonstrated.

## 67.1 Remaining R1.2 validation

Before R1.3 begins, run a real local smoke test using:

```
Qwen/Qwen3-Embedding-0.6B
```

The smoke test must demonstrate:

1. the model loads successfully in the current Terminal Agent environment,
2. a SearchDocument can be embedded,
3. a retrieval query can be embedded,
4. document/query vector dimensions are correct and equal,
5. batch embedding works,
6. document/query encoding remain distinct,
7. no unexpected dependency or device failure occurs.

Only after this validation is R1.2 considered fully complete.

---

# 68. Immediate Next Step

The next action is **R1.2 real-provider smoke validation**, not R1.3 implementation.

```
R1.2 unit boundary       COMPLETE
        ↓
R1.2 real Qwen smoke     ← NEXT
        ↓
R1.2 completion
        ↓
R1.3 Dense Semantic Retrieval
```

R1.3 begins only after the selected embedding provider is proven in the actual Terminal Agent environment.

---

# 69. R1.2 Completion — Real Provider Validation

**Status:** COMPLETE

R1.2 is now validated end-to-end at the embedding-provider boundary.

## 69.1 Real-provider smoke validation

The selected local provider was tested using:

```
Ollama
  ↓
qwen3-embedding:0.6b
  ↓
Qwen3EmbeddingProvider
```

The real smoke test passed:

```
1 passed in 51.32s
```

Observed semantic sanity-check scores:

```
relevant_similarity   = 0.7758466947569013
unrelated_similarity = 0.3184739954223959
```

The relevant document therefore scored substantially higher than the unrelated document for the test query.

The smoke validation demonstrated that:

- Ollama is reachable from the Terminal Agent environment.
- `qwen3-embedding:0.6b` loads and serves embeddings successfully.
- SearchDocument text can be embedded through the provider.
- Query text can be embedded through the provider.
- Document and query vectors have the configured dimension.
- Batch embedding works.
- The provider produces finite normalized vectors.
- The semantic sanity check distinguishes a relevant document from an unrelated document.

## 69.2 R1.2 final status

The R1.2 implementation and validation boundary is now:

```
EvidenceRecord
      ↓
DeterministicSearchDocumentBuilder
      ↓
SearchDocument
      ↓
Qwen3EmbeddingProvider
      ↓
Ollama / qwen3-embedding:0.6b
      ↓
Validated embedding vector
```

R1.2 is therefore considered complete.

---

# 70. R1.3 — Dense Semantic Retrieval

**Status:** NEXT

R1.3 starts from the validated embedding boundary and introduces the first actual dense retrieval implementation.

Target flow:

```
SearchDocument
      ↓
Qwen3EmbeddingProvider
      ↓
Vector
      ↓
DenseIndex
      ↓
Similarity Search
      ↓
RetrievedEvidence
```

R1.3 should introduce only:

- dense index implementation,
- document/vector upsert,
- query embedding,
- similarity search,
- thread-scoped filtering,
- score/rank mapping,
- focused retrieval tests.

R1.3 should not yet introduce:

- BM25,
- RRF,
- reranking,
- MMR,
- multi-hop retrieval,
- retrieval-trigger policy,
- Context Builder integration.

## 70.1 R1.3 implementation principle

The first dense retrieval implementation must validate the retrieval architecture independently of lexical search and reranking.

The central question is:

> Can the Terminal Agent retrieve the correct retained Evidence from a bounded thread using semantic similarity?

Only after that boundary is measured should lexical retrieval and hybrid fusion be added.

---

# 71. Retrieval Progress Status

```
R1.1 Contracts & Representation       COMPLETE
R1.2 Projection + Embedding           COMPLETE
R1.3 Dense Semantic Retrieval         NEXT
R1.4 Lexical / BM25                   PLANNED
R1.5 RRF Fusion                       PLANNED
R1.6 Evaluation                       PLANNED
R1.7 Integration                      PLANNED
```

The selected embedding provider for the current prototype is:

```
Qwen/Qwen3-Embedding-0.6B
served locally through Ollama
```

This remains replaceable behind `EmbeddingProvider`.

---

# 71. R1.3 — Dense Semantic Retrieval Design

**Status:** Design locked; implementation starts with R1.3-A/B.

R1.3 introduces the first actual semantic retrieval capability using the validated R1.2 embedding boundary.

## 71.1 Core question

Can the Terminal Agent retrieve the correct retained Evidence from a bounded thread using dense semantic similarity?

R1.3 deliberately stops before lexical retrieval, fusion, reranking, diversity selection, multi-hop retrieval, retrieval-trigger policy, and Context Builder integration.

## 71.2 Correct dependency boundary

EvidenceStore → SearchDocumentBuilder → SearchDocument → EmbeddingProvider → DenseIndex → DenseSearchHit[] → DenseSemanticRetriever → EvidenceStore.get() → RetrievedEvidence[] → EvidenceRetrievalResult

The DenseIndex must return index-level search hits, not RetrievedEvidence. RetrievedEvidence is a public retrieval result; EvidenceStore remains the authoritative source of EvidenceRecord objects.

## 71.3 DenseSearchHit

R1.3 introduces an index-level result containing:

- document_id
- score
- rank

The DenseIndex knows only searchable document identity and ranking information. It does not own authoritative EvidenceRecord instances.

## 71.4 DenseIndex responsibility

DenseIndex supports:

- upserting SearchDocuments with vectors,
- thread-scoped semantic search,
- bounded candidate retrieval.

DenseIndex does not:

- access EvidenceStore,
- construct RetrievedEvidence,
- perform higher-level relevance decisions,
- perform reranking,
- perform lexical retrieval.

## 71.5 Dense indexing lifecycle

EvidenceRecord → SearchDocumentBuilder → SearchDocument → EmbeddingProvider.embed_documents() → DenseIndex.upsert()

Indexing is derived from authoritative Evidence. If indexing fails, retained Evidence remains intact.

## 71.6 Dense query lifecycle

EvidenceRetrievalQuery → EmbeddingProvider.embed_queries() → query vector → DenseIndex.search() → DenseSearchHit[] → EvidenceStore.get() → RetrievedEvidence[] → EvidenceRetrievalResult

The DenseSemanticRetriever resolves search hits back to authoritative Evidence.

## 71.7 Thread isolation

Thread scope is enforced at the DenseIndex boundary. A query for thread A must search only vectors belonging to thread A rather than searching all vectors and filtering after ranking.

## 71.8 Similarity

R1.3 initially uses cosine similarity. The R1.2 provider is configured for normalized vectors, making cosine similarity appropriate for the initial implementation.

No hard relevance threshold is introduced in R1.3. Score thresholds are deferred until R1.6 provides evidence about real score distributions.

## 71.9 Top-K

The public query exposes limit. R1.3 initially uses that limit for dense candidate retrieval. Later R2 reranking may introduce a larger candidate pool, but R1.3 does not need that complexity yet.

## 71.10 Chunk handling

Search operates at SearchDocument level. If one EvidenceRecord later produces multiple chunks, R1.3 does not collapse them by evidence_id. Deduplication and diversity are deferred to R3.

## 71.11 Evidence resolution

DenseSearchHit identifies a stable document_id. The retriever resolves that document to its evidence_id and fetches the authoritative EvidenceRecord from EvidenceStore.

If an index hit cannot be resolved to retained Evidence, the system must surface an explicit index-consistency problem rather than fabricate RetrievedEvidence.

## 71.12 Dense backend

The initial backend candidate is Qdrant in local/self-hosted mode.

LanceDB-specific types must remain inside the DenseIndex implementation. The current table direction is terminal_agent_evidence, with thread_id stored as searchable metadata rather than one table per thread.

## 71.13 Source-of-truth invariant

EvidenceStore is authoritative. DenseIndex is derived state.

EvidenceStore healthy + DenseIndex unavailable means Evidence remains retained while retrieval may be unavailable.

DenseIndex hit + EvidenceStore missing means an orphaned search result and must be observable as an index-consistency failure.

---

# 72. R1.3 Implementation Subphases

## R1.3-A — DenseIndex Contract Correction

Change the contract from DenseIndex returning RetrievedEvidence to DenseIndex returning DenseSearchHit.

Exit condition: DenseIndex depends only on search-document/index abstractions and has no EvidenceStore dependency.

## R1.3-B — DenseSearchHit Model

Add document_id, score, and rank with rank validation.

Exit condition: the model is usable by DenseIndex without importing EvidenceStore.

## R1.3-C — LanceDB Dense Index

Implement local persistent LanceDB initialization, table creation, vector upsert, metadata construction, thread filtering, and cosine similarity search.

Exit condition: SearchDocuments can be written and semantically searched within a thread.

## R1.3-D — DenseIndexer Write Path

Implement the orchestration from EvidenceRecord to SearchDocument to embedding to DenseIndex.upsert().

Exit condition: retained Evidence can be indexed through one deterministic write path.

## R1.3-E — DenseSemanticRetriever

Implement query embedding, DenseIndex search, hit resolution, EvidenceStore lookup, and RetrievedEvidence construction.

Exit condition: the public EvidenceRetriever contract returns ranked authoritative Evidence from dense hits.

## R1.3-F — Thread/Scope Filtering

Prove that semantic search cannot cross thread boundaries.

Exit condition: cross-thread leakage is absent through the normal DenseIndex path.

## R1.3-G — Evidence Resolution & Consistency

Validate successful hit resolution and explicit handling of orphaned index results.

Exit condition: the source-of-truth boundary is preserved under normal and failure conditions.

## R1.3-H — Dense Retrieval Tests

Cover upsert/search, semantic relevance, ranking, limit, thread isolation, evidence resolution, orphan detection, and index-failure preservation of Evidence.

Exit condition: R1.3 dense retrieval behavior is reproducible and measurable.

---

# 73. R1.3 Non-Goals

R1.3 does not include BM25, RRF, reranking, MMR, context compression, query rewriting, LLM retrieval routing, multi-hop retrieval, automatic retrieval triggers, or runtime graph modification.

---

# 74. R1.3 Invariants

1. DenseIndex never returns authoritative EvidenceRecord objects.
2. DenseIndex returns only index-level search hits.
3. EvidenceStore remains the source of truth.
4. DenseIndex is derived state.
5. Dense retrieval is thread/scope aware.
6. No arbitrary relevance threshold is introduced in R1.3.
7. Similarity scores remain observable.
8. Evidence resolution happens after index search.
9. Missing Evidence for a search hit is an explicit consistency problem.
10. Index failure never deletes or mutates retained Evidence.
11. LanceDB-specific types do not leak outside the DenseIndex implementation.
12. R1.3 operates at SearchDocument level; chunk deduplication is deferred.
13. The existing Prototype 2 runtime architecture remains unchanged.

---

# 75. Immediate R1.3 Work Order

R1.3-A → R1.3-B → R1.3-C → R1.3-D → R1.3-E → R1.3-F → R1.3-G → R1.3-H

The first coding patch contains only R1.3-A and R1.3-B.