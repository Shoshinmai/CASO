from __future__ import annotations

from agents.terminal.runtime.concurrent_task_executor import (
    ConcurrentTaskExecutor,
)
from agents.terminal.runtime.task_execution_coordinator import (
    TaskExecutionCoordinator,
)
from agents.terminal.runtime.task_runner import (
    AsyncTaskRunner,
)
from agents.terminal.task_executor.task_worker import (
    TaskWorker,
)
from agents.terminal.state import TerminalState


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
    - return the reconciled TaskPlan

    This node does not:
    - mutate individual TaskItems directly
    - execute a single shared ExecutionWorkflow
    - use TerminalState.execution_workflow as the active
      concurrent-workflow container
    - run the existing single-task Critic lifecycle
    """

    task_plan = state.get(
        "task_plan",
    )

    if task_plan is None:
        raise ValueError(
            "Cannot start concurrent execution without "
            "a TaskPlan."
        )

    # ==========================================================
    # Build task-local execution stack
    # ==========================================================

    worker = TaskWorker()

    runner = AsyncTaskRunner(
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

    updated_plan = await coordinator.execute_plan(
        plan=task_plan,
        state=state,
    )

    # ==========================================================
    # Return only authoritative concurrent execution state
    # ==========================================================

    return {
        "task_plan": updated_plan,
        "execution_workflow": None,
    }