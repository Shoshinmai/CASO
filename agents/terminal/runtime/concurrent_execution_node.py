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
    Execute the current TaskPlan through the concurrent
    task-execution coordinator.

    This node is the graph adapter for the Prototype 1 concurrent
    execution path.

    Responsibilities:
    - receive the authoritative TaskPlan from TerminalState
    - construct the concurrent execution stack
    - execute dependency-aware task waves
    - receive the final coordinated execution result
    - build the deterministic PlanExecutionOutcome
    - notify the Runtime that execution reached a stable review
      boundary

    This node does not:
    - mutate individual TaskItems directly
    - execute a single shared ExecutionWorkflow
    - use TerminalState.execution_workflow as the active
      concurrent-workflow container
    - run the Critic
    - make semantic decisions
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
    # Build task-local execution stack
    # ==========================================================

    worker = TaskWorker()

    runner = TaskRunner(
        worker=worker,
    )

    executor = ConcurrentTaskExecutor(
        runner=runner,
        max_concurrency=3,
    )

    coordinator = TaskExecutionCoordinator(
        executor=executor,
    )

    # ==========================================================
    # Execute dependency-aware waves
    # ==========================================================

    coordinated_execution = (
        await coordinator.execute_plan(
            plan=task_plan,
            state=state,
        )
    )

    updated_plan = coordinated_execution.plan

    # ==========================================================
    # Build the deterministic plan-level execution snapshot.
    #
    # At this point every admitted execution wave has completed
    # and its results have been reconciled.
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
    # Concurrent execution has reached a stable review boundary.
    #
    # The Runtime Kernel owns the state transition:
    #
    #     EXECUTING
    #          ↓
    #     EXECUTION_COMPLETED
    #          ↓
    #      REVIEWING
    #
    # The Critic will be invoked by the graph after this node.
    # ==========================================================

    RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.EXECUTION_COMPLETED,
    )

    # ==========================================================
    # Return authoritative concurrent execution state
    # ==========================================================

    return {
        "task_plan": updated_plan,

        "plan_execution_outcome": (
            plan_execution_outcome
        ),

        # The concurrent path does not use the singular
        # ExecutionWorkflow slot.
        "execution_workflow": None,

        "runtime_state": runtime_state,
    }