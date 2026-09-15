from __future__ import annotations

from abc import ABC, abstractmethod

from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
)
from agents.terminal.task_plan.models import TaskItem


class AsyncTaskRunner(ABC):
    """
    Async execution boundary for one TaskExecutionContext.
    """

    @abstractmethod
    async def execute_task(
        self,
        context: TaskExecutionContext,
        *,
        task: TaskItem,
        state: dict,
    ) -> TaskExecutionResult:
        """
        Execute one explicitly assigned task asynchronously.

        The caller owns task admission and supplies the task
        snapshot and task-local execution state.

        The runner/worker must not mutate central TaskPlan state.
        """

        raise NotImplementedError
    
    