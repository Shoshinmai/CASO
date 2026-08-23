from __future__ import annotations

from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
)
from agents.terminal.runtime.task_runner import (
    AsyncTaskRunner,
)
from agents.terminal.task_executor.task_worker import (
    TaskWorker,
)
from agents.terminal.task_plan.models import TaskItem


class TaskRunner(AsyncTaskRunner):
    """
    Concrete adapter between AsyncTaskRunner and TaskWorker.
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

        return await self.worker.execute(
            state=state,
            task_execution=context,
            task=task,
        )