from __future__ import annotations

from agents.terminal.runtime.concurrent_task_executor import (
    ConcurrentTaskExecutor,
)
from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.plan_execution_outcome import (
    build_plan_execution_outcome,
)
from agents.terminal.runtime.kernel import RuntimeKernel
from agents.terminal.runtime.task_execution_coordinator import (
    TaskExecutionCoordinator,
)
from agents.terminal.runtime.task_runner_impl import (
    TaskRunner,
)
from agents.terminal.state import TerminalState
from agents.terminal.task_executor.task_worker import (
    TaskWorker,
)


async def concurrent_execution_node(
    state: TerminalState,
) -> dict:
    """
    Execute exactly one concurrent execution wave.

    This node is the graph boundary between:

        concurrent worker execution
                ↓
        wave reconciliation
                ↓
              Critic

    The coordinator intentionally executes only the current READY
    wave. Newly-ready dependent tasks are returned to the Runtime
    rather than being automatically executed in this invocation.

    Workers operate on isolated task-local snapshots.

    The coordinator/reconciler owns the authoritative state
    transition after the complete wave.
    """

    task_plan = state.get(
        "task_plan",
    )

    if task_plan is None:
        raise ValueError(
            "Cannot start concurrent execution without "
            "a TaskPlan."
        )

    runtime_state = state.get(
        "runtime_state",
    )

    if runtime_state is None:
        raise ValueError(
            "Cannot start concurrent execution without "
            "RuntimeState."
        )

    # ==========================================================
    # TEMPORARY DEBUGGING
    # ==========================================================

    print()
    print("=" * 72)
    print("              CONCURRENT WAVE START")
    print("=" * 72)

    print(
        f"Plan: {task_plan.plan_id}"
    )

    print(
        f"Goal: {task_plan.goal}"
    )

    ready_tasks = [
        task
        for task in task_plan.tasks
        if task.status.value == "ready"
    ]

    print()
    print(
        "READY tasks admitted for this wave: "
        f"{len(ready_tasks)}"
    )

    print(
        "READY task IDs: "
        f"{[task.task_id for task in ready_tasks]}"
    )

    print(
        "Max concurrency: 3"
    )

    print()
    print("=" * 72)
    print("              EXECUTING CURRENT WAVE")
    print("=" * 72)

    # ==========================================================
    # Build concurrent execution stack
    # ==========================================================
    #
    # ConcurrentTaskExecutor creates an isolated Worker/Runner
    # execution stack for every task in the wave.
    # ==========================================================

    executor = ConcurrentTaskExecutor(
        runner=TaskRunner(
            worker=TaskWorker(),
        ),
        max_concurrency=3,
    )

    coordinator = TaskExecutionCoordinator(
        executor=executor,
    )

    # ==========================================================
    # Execute ONE dependency-aware wave
    # ==========================================================

    coordinated_execution = (
        await coordinator.execute_plan(
            plan=task_plan,
            state=state,
        )
    )

    updated_plan = coordinated_execution.plan

    # ==========================================================
    # Build deterministic post-wave execution snapshot
    # ==========================================================

    plan_execution_outcome = (
        build_plan_execution_outcome(
            task_plan=updated_plan,
            task_results=(
                coordinated_execution.task_results
            ),
        )
    )

    # ==========================================================
    # Wave finished
    # ==========================================================

    print()
    print("=" * 72)
    print("              CONCURRENT WAVE END")
    print("=" * 72)

    print()
    print("Wave results:")

    for result in coordinated_execution.task_results:

        print(
            f"  {result.task_id}"
            f" | status={result.status.value}"
            f" | processing_results="
            f"{len(result.processing_results)}"
        )

    newly_ready = [
        task
        for task in updated_plan.tasks
        if task.status.value == "ready"
    ]

    print()
    print(
        "READY tasks after reconciliation: "
        f"{[task.task_id for task in newly_ready]}"
    )

    print(
        "Plan condition after wave: "
        f"{plan_execution_outcome.condition.value}"
    )

    print(
        "Active memory after wave reconciliation:"
    )

    active_memory = state.get(
        "active_memory",
    )

    if active_memory is not None:

        print(
            f"  known_facts="
            f"{len(active_memory.known_facts)}"
        )

        print(
            f"  discovered_resources="
            f"{len(active_memory.discovered_resources)}"
        )

        print(
            f"  completed_work="
            f"{len(active_memory.completed_work)}"
        )

        print(
            f"  unresolved_needs="
            f"{len(active_memory.unresolved_needs)}"
        )

    else:

        print(
            "  WARNING: active_memory missing."
        )

    # ==========================================================
    # MOVE RUNTIME INTO REVIEWING
    # ==========================================================
    #
    # This is the critical synchronization boundary.
    #
    # Even when reconciliation makes a dependent task READY,
    # that task is NOT executed here.
    #
    # The graph returns to the Critic first.
    # ==========================================================

    next_stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.EXECUTION_COMPLETED,
    )

    print()
    print(
        "[CONCURRENT WAVE] "
        "Runtime transition:"
    )

    print(
        f"  event="
        f"{RuntimeEvent.EXECUTION_COMPLETED.value}"
    )

    print(
        f"  mode="
        f"{runtime_state.mode.value}"
    )

    print(
        f"  next_stage="
        f"{next_stage.value}"
    )

    print(
        f"  last_event="
        f"{runtime_state.last_event.value}"
    )

    # ==========================================================
    # AUTHORITATIVE GRAPH STATE PROPAGATION
    # ==========================================================
    #
    # The reconciler has already mutated these objects.
    # Return the authoritative post-wave state explicitly.
    # ==========================================================

    return {
        "task_plan": updated_plan,

        "plan_execution_outcome": (
            plan_execution_outcome
        ),

        "active_memory": state[
            "active_memory"
        ],

        "artifact_references": state[
            "artifact_references"
        ],

        "execution_memory": state[
            "execution_memory"
        ],

        "execution_workflow": None,

        "runtime_state": runtime_state,

        # Clear stale Critic output from an earlier review.
        "critic_output": None,

        "critic_runtime_event": None,
    }