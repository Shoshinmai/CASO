from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.models import (
    RuntimeDecisionContext,
    RuntimeEvidence,
    RuntimeState,
)
from agents.terminal.runtime.nodes import (
    _apply_concurrent_critic_decision,
)
from agents.terminal.task_plan.models import (
    TaskItem,
    TaskItemStatus,
    TaskPlan,
    TaskPlanStatus,
)


def context(
    scope: str,
    targets: list[str] | None = None,
):
    return RuntimeDecisionContext(
        rationale="Test rationale.",
        evidence=[
            RuntimeEvidence(
                source="test",
                observation="Test evidence.",
            )
        ],
        decision_scope=scope,
        target_task_ids=targets or [],
    )


def make_plan():
    return TaskPlan(
        plan_id="d6-2-test",
        goal="Test concurrent Critic decision application.",
        status=TaskPlanStatus.CREATED,
        tasks=[
            TaskItem(
                task_id="task-A",
                objective="Task A",
                status=TaskItemStatus.FAILED,
                dependencies=[],
            ),
            TaskItem(
                task_id="task-B",
                objective="Task B",
                status=TaskItemStatus.COMPLETED,
                dependencies=[],
            ),
            TaskItem(
                task_id="task-C",
                objective="Task C",
                status=TaskItemStatus.BLOCKED,
                dependencies=["task-A"],
            ),
        ],
        metadata={},
    )


def make_state():
    return {
        "task_plan": make_plan(),
        "plan_execution_outcome": "test-outcome",
        "execution_workflow": "test-workflow",
        "runtime_state": RuntimeState(),
        "critic_runtime_event": None,
        "ephemeral_execution_state": None,
    }


# ==========================================================
# 1. RETRY_TASK
# ==========================================================

print("\n========== 1. RETRY_TASK ==========\n")

state = make_state()

# The concurrent execution boundary must already be in REVIEWING.
state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.RETRY_TASK,
    decision_context=context(
        "task",
        ["task-A"],
    ),
    runtime_state=state["runtime_state"],
)

task_a = state["task_plan"].tasks[0]

print(
    "task-A:",
    task_a.status.value,
)

print(
    "outcome:",
    result["plan_execution_outcome"],
)

print(
    "workflow:",
    result["execution_workflow"],
)

print(
    "runtime:",
    result["runtime_state"].mode,
)

assert task_a.status == TaskItemStatus.READY
assert result["plan_execution_outcome"] is None
assert result["execution_workflow"] is None


# ==========================================================
# 2. MULTI-TASK RETRY
# ==========================================================

print("\n========== 2. MULTI-TASK RETRY ==========\n")

state = make_state()

# Make B failed as well for this test.
state["task_plan"].tasks[1].status = TaskItemStatus.FAILED

state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.RETRY_TASK,
    decision_context=context(
        "task",
        ["task-A", "task-B"],
    ),
    runtime_state=state["runtime_state"],
)

for task in state["task_plan"].tasks:
    print(
        task.task_id,
        "->",
        task.status.value,
    )

assert (
    state["task_plan"].tasks[0].status
    == TaskItemStatus.READY
)

assert (
    state["task_plan"].tasks[1].status
    == TaskItemStatus.READY
)

assert (
    result["plan_execution_outcome"]
    is None
)


# ==========================================================
# 3. TASK_COMPLETED
# ==========================================================

print("\n========== 3. TASK_COMPLETED ==========\n")

state = make_state()

state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.TASK_COMPLETED,
    decision_context=context(
        "task",
        ["task-B"],
    ),
    runtime_state=state["runtime_state"],
)

print(
    "task-B:",
    state["task_plan"].tasks[1].status.value,
)

assert (
    state["task_plan"].tasks[1].status
    == TaskItemStatus.COMPLETED
)

assert (
    result["plan_execution_outcome"]
    is None
)


# ==========================================================
# 4. PLAN_UPDATE_REQUIRED
# ==========================================================

print("\n========== 4. PLAN_UPDATE_REQUIRED ==========\n")

state = make_state()

state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.PLAN_UPDATE_REQUIRED,
    decision_context=context(
        "plan",
    ),
    runtime_state=state["runtime_state"],
)

print(
    "runtime:",
    result["runtime_state"].mode,
)

print(
    "outcome preserved:",
    result["plan_execution_outcome"],
)

print(
    "workflow:",
    result["execution_workflow"],
)

assert (
    result["plan_execution_outcome"]
    == "test-outcome"
)

assert result["execution_workflow"] is None


# ==========================================================
# 5. REPLAN_REQUIRED
# ==========================================================

print("\n========== 5. REPLAN_REQUIRED ==========\n")

state = make_state()

state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.REPLAN_REQUIRED,
    decision_context=context(
        "plan",
    ),
    runtime_state=state["runtime_state"],
)

print(
    "runtime:",
    result["runtime_state"].mode,
)

print(
    "outcome preserved:",
    result["plan_execution_outcome"],
)

assert (
    result["plan_execution_outcome"]
    == "test-outcome"
)


# ==========================================================
# 6. GOAL_COMPLETED
# ==========================================================

print("\n========== 6. GOAL_COMPLETED ==========\n")

state = make_state()

state["runtime_state"].mode = "reviewing"

result = _apply_concurrent_critic_decision(
    state=state,
    event=RuntimeEvent.GOAL_COMPLETED,
    decision_context=context(
        "goal",
    ),
    runtime_state=state["runtime_state"],
)

print(
    "runtime:",
    result["runtime_state"].mode,
)

print(
    "workflow:",
    result["execution_workflow"],
)

assert result["execution_workflow"] is None


# ==========================================================
# COMPLETE
# ==========================================================

print(
    "\n========== D.6.2 DIRECT TEST COMPLETE ==========\n"
)

print(
    "All concurrent Critic decision application cases passed."
)