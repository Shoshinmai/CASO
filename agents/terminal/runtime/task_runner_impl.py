from __future__ import annotations

from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
)
from agents.terminal.runtime.task_runner import (
    AsyncTaskRunner,
)
from agents.terminal.runtime.task_state_snapshot import (
    build_task_execution_snapshot,
)
from agents.terminal.task_executor.task_worker import (
    TaskWorker,
)
from agents.terminal.task_plan.models import TaskItem


class TaskRunner(AsyncTaskRunner):
    """
    Concrete adapter between AsyncTaskRunner and TaskWorker.

    The runner constructs the isolated state snapshot for the
    assigned task and then delegates execution to TaskWorker.
    """

    def __init__(
        self,
        *,
        worker: TaskWorker | None = None,
    ) -> None:

        self.worker = (
            worker
            if worker is not None
            else TaskWorker()
        )

    async def execute_task(
        self,
        context: TaskExecutionContext,
        *,
        task: TaskItem,
        state: dict,
    ) -> TaskExecutionResult:

        task_state = build_task_execution_snapshot(
            state=state,
            task=task,
        )

        return await self.worker.execute(
            state=task_state,
            task_execution=context,
            task=task,
        )