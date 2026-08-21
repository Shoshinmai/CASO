from __future__ import annotations

from abc import ABC, abstractmethod

from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
)


class AsyncTaskRunner(ABC):
    """
    Async execution boundary for one TaskExecutionContext.

    One runner invocation owns exactly one task execution.

    The runner may:
    - construct a workflow
    - execute workflow steps sequentially
    - invoke async tools
    - create and finalize execution attempts
    - collect task-local results

    The runner must not:
    - directly schedule other tasks
    - mutate unrelated TaskItems
    - decide global concurrency
    - own TaskPlan scheduling policy

    Those responsibilities belong to TaskScheduler and
    TaskPlanManager.
    """

    @abstractmethod
    async def execute_task(
        self,
        context: TaskExecutionContext,
    ) -> TaskExecutionResult:
        """
        Execute one task asynchronously.

        The returned result must correspond to the supplied execution
        context.

        This method represents the complete lifecycle of one task from
        execution start until terminal completion, failure, or
        cancellation.
        """

        raise NotImplementedError