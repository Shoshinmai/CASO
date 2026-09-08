from __future__ import annotations

import asyncio

from agents.terminal.runtime.concurrent_debug import (
    ConcurrentDebugSession,
)

from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
    TaskExecutionStatus,
)

from agents.terminal.runtime.task_runner import (
    AsyncTaskRunner,
)

from agents.terminal.task_plan.models import TaskItem


class ConcurrentTaskExecutor:
    """
    Execute an explicitly supplied batch of independent tasks
    concurrently.

    This class does not:
    - discover READY tasks
    - mutate TaskPlan state
    - resolve dependencies
    - release dependent tasks
    - perform result aggregation into the central plan

    It only executes the supplied execution wave and returns
    one TaskExecutionResult per task.

    Temporary debugging:
    - opens one Windows Terminal monitor tab per worker
    - writes worker lifecycle events to per-task JSONL logs
    """

    def __init__(
        self,
        *,
        runner: AsyncTaskRunner,
        max_concurrency: int = 3,
    ) -> None:

        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1.")

        self.runner = runner
        self.max_concurrency = max_concurrency

    async def execute(
        self,
        *,
        plan_id: str,
        tasks: list[TaskItem],
        state: dict,
    ) -> list[TaskExecutionResult]:
        """
        Execute one explicit task wave concurrently.

        Every task receives its own TaskExecutionContext.
        TaskRunner creates the task-local state snapshot.
        """

        if not tasks:
            return []

        semaphore = asyncio.Semaphore(self.max_concurrency)

        # ======================================================
        # TEMPORARY CONCURRENT DEBUGGING
        # ======================================================
        #
        # The debug session does NOT execute the tasks.
        #
        # It only opens PowerShell/Windows Terminal tabs that
        # observe the real asyncio workers.
        #
        debug_session = ConcurrentDebugSession(
            plan_id=plan_id,
            tasks=tasks,
        )

        debug_session.open_tabs(
            tasks=tasks,
        )

        for task in tasks:
            debug_session.write(
                task_id=task.task_id,
                event="WAVE_START",
                message=(f"Concurrent wave started with " f"{len(tasks)} task(s)."),
                plan_id=plan_id,
                task_count=len(tasks),
            )

        async def execute_one(
            task: TaskItem,
        ) -> TaskExecutionResult:

            async with semaphore:

                context = TaskExecutionContext(
                    plan_id=plan_id,
                    task_id=task.task_id,
                    status=TaskExecutionStatus.CREATED,
                    metadata={
                        "task_objective": task.objective,
                    },
                )

                debug_session.write(
                    task_id=task.task_id,
                    event="START",
                    message=("Worker entered concurrent execution."),
                    objective=task.objective,
                )

                try:

                    debug_session.write(
                        task_id=task.task_id,
                        event="RUNNING",
                        message=("TaskRunner execution started."),
                    )

                    result = await self.runner.execute_task(
                        context,
                        task=task,
                        state=state,
                    )

                    debug_session.write(
                        task_id=task.task_id,
                        event="RESULT",
                        message=("TaskRunner returned a result."),
                        status=result.status.value,
                        execution_id=result.execution_id,
                        workflow_id=result.workflow_id,
                    )

                    debug_session.close_worker(
                        task_id=task.task_id,
                        status=result.status.value,
                    )

                    return result

                except asyncio.CancelledError:

                    context.status = TaskExecutionStatus.CANCELLED

                    context.error = "Task execution was cancelled."

                    debug_session.close_worker(
                        task_id=task.task_id,
                        status="cancelled",
                        error=context.error,
                    )

                    raise

                except Exception as error:

                    context.status = TaskExecutionStatus.FAILED

                    context.error = str(error)

                    debug_session.write(
                        task_id=task.task_id,
                        event="ERROR",
                        message=("TaskRunner raised an exception."),
                        error=str(error),
                    )

                    result = TaskExecutionResult(
                        execution_id=(context.execution_id),
                        plan_id=context.plan_id,
                        task_id=context.task_id,
                        status=(TaskExecutionStatus.FAILED),
                        workflow_id=(
                            context.workflow.workflow_id
                            if context.workflow is not None
                            else None
                        ),
                        result=context.result,
                        error=str(error),
                        metadata=context.metadata,
                    )

                    debug_session.close_worker(
                        task_id=task.task_id,
                        status="failed",
                        error=str(error),
                    )

                    return result

        # ======================================================
        # REAL CONCURRENT EXECUTION
        # ======================================================
        #
        # Nothing about the actual concurrency mechanism has
        # changed.
        #
        # Every execute_one() coroutine is still scheduled
        # concurrently through asyncio.gather().
        #

        raw_results = await asyncio.gather(
            *(execute_one(task) for task in tasks),
            return_exceptions=True,
        )

        results: list[TaskExecutionResult] = []

        for task, raw_result in zip(
            tasks,
            raw_results,
        ):

            if isinstance(
                raw_result,
                TaskExecutionResult,
            ):

                results.append(raw_result)

                continue

            if isinstance(
                raw_result,
                asyncio.CancelledError,
            ):

                results.append(
                    TaskExecutionResult(
                        execution_id="",
                        plan_id=plan_id,
                        task_id=task.task_id,
                        status=(TaskExecutionStatus.CANCELLED),
                        error=("Task execution was cancelled."),
                    )
                )

                continue

            if isinstance(
                raw_result,
                Exception,
            ):

                results.append(
                    TaskExecutionResult(
                        execution_id="",
                        plan_id=plan_id,
                        task_id=task.task_id,
                        status=(TaskExecutionStatus.FAILED),
                        error=str(raw_result),
                    )
                )

                continue

            raise TypeError(
                "Concurrent task executor received an "
                "unexpected result type: "
                f"{type(raw_result)!r}"
            )

        # ======================================================
        # TEMPORARY DEBUGGING: print wave completion
        # ======================================================

        for result in results:

            debug_session.write(
                task_id=result.task_id,
                event="RECONCILED",
                message=("Task result collected by " "ConcurrentTaskExecutor."),
                status=result.status.value,
            )

        return results
