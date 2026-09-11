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

from agents.terminal.runtime.task_runner_impl import (
    TaskRunner,
)

from agents.terminal.task_executor.task_worker import (
    TaskWorker,
)

from agents.terminal.task_plan.models import (
    TaskItem,
)


class ConcurrentTaskExecutor:
    """
    Execute an explicitly supplied batch of independent tasks
    concurrently.

    Each task receives its own TaskWorker / TaskRunner /
    WorkflowRuntime stack.

    This is important because worker execution is task-local.
    Sharing one TaskWorker or WorkflowRuntime across concurrent
    tasks unnecessarily couples their runtime objects.

    This class does not:
    - discover READY tasks
    - mutate TaskPlan state
    - resolve dependencies
    - release dependent tasks
    - perform central result reconciliation

    It only executes the supplied execution wave and returns
    one TaskExecutionResult per task.
    """

    def __init__(
        self,
        *,
        runner: AsyncTaskRunner,
        max_concurrency: int = 3,
    ) -> None:

        if max_concurrency < 1:
            raise ValueError(
                "max_concurrency must be at least 1."
            )

        self.runner = runner
        self.max_concurrency = max_concurrency

    async def execute(
        self,
        *,
        plan_id: str,
        tasks: list[TaskItem],
        state: dict,
    ) -> list[TaskExecutionResult]:

        if not tasks:
            return []

        semaphore = asyncio.Semaphore(
            self.max_concurrency
        )

        # ======================================================
        # TEMPORARY CONCURRENT DEBUGGING
        # ======================================================

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
                message=(
                    "Concurrent wave started with "
                    f"{len(tasks)} task(s)."
                ),
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

                # ==================================================
                # IMPORTANT:
                #
                # Every concurrent task gets its OWN execution
                # stack.
                #
                # Before this change:
                #
                #     one TaskWorker
                #          ↓
                #     one TaskRunner
                #          ↓
                #     one WorkflowRuntime
                #
                # was shared by every worker.
                #
                # Now:
                #
                #     Task A → Worker A → Runner A → Runtime A
                #     Task B → Worker B → Runner B → Runtime B
                #     Task C → Worker C → Runner C → Runtime C
                #
                # The debug session remains shared intentionally
                # because it is only a logging coordinator.
                # ==================================================

                worker = TaskWorker(
                    debug_session=debug_session,
                )

                runner = TaskRunner(
                    worker=worker,
                    debug_session=debug_session,
                )

                debug_session.write(
                    task_id=task.task_id,
                    event="START",
                    message=(
                        "Worker entered concurrent execution."
                    ),
                    objective=task.objective,
                )

                try:

                    context.status = (
                        TaskExecutionStatus.RUNNING
                    )

                    debug_session.write(
                        task_id=task.task_id,
                        event="RUNNING",
                        message=(
                            "TaskRunner execution started."
                        ),
                    )

                    # --------------------------------------------------
                    # Explicit marker immediately before the LLM call
                    # is reached inside TaskWorker.
                    # --------------------------------------------------

                    debug_session.write(
                        task_id=task.task_id,
                        event="WORKER_DISPATCH",
                        message=(
                            "Dispatching isolated worker "
                            "execution stack."
                        ),
                    )

                    result = await runner.execute_task(
                        context,
                        task=task,
                        state=state,
                    )

                    debug_session.write(
                        task_id=task.task_id,
                        event="RESULT",
                        message=(
                            "TaskRunner returned a result."
                        ),
                        status=result.status.value,
                        execution_id=result.execution_id,
                        workflow_id=result.workflow_id,
                        processing_results=len(
                            result.processing_results
                        ),
                    )

                    debug_session.close_worker(
                        task_id=task.task_id,
                        status=result.status.value,
                    )

                    return result

                except asyncio.CancelledError:

                    context.status = (
                        TaskExecutionStatus.CANCELLED
                    )

                    context.error = (
                        "Task execution was cancelled."
                    )

                    debug_session.write(
                        task_id=task.task_id,
                        event="CANCELLED",
                        message=(
                            "Worker task was cancelled."
                        ),
                    )

                    debug_session.close_worker(
                        task_id=task.task_id,
                        status="cancelled",
                        error=context.error,
                    )

                    raise

                except Exception as error:

                    context.status = (
                        TaskExecutionStatus.FAILED
                    )

                    context.error = str(error)

                    debug_session.write(
                        task_id=task.task_id,
                        event="ERROR",
                        message=(
                            "TaskRunner raised an exception."
                        ),
                        error=str(error),
                    )

                    result = TaskExecutionResult(
                        execution_id=context.execution_id,
                        plan_id=context.plan_id,
                        task_id=context.task_id,
                        status=(
                            TaskExecutionStatus.FAILED
                        ),
                        workflow_id=(
                            context.workflow.workflow_id
                            if context.workflow is not None
                            else None
                        ),
                        result=context.result,
                        error=str(error),
                        metadata=context.metadata,
                        processing_results=[],
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
        # All execute_one() coroutines are scheduled together.
        #
        # The semaphore limits the number of active workers but
        # does NOT serialize them.
        # ======================================================

        print()
        print(
            "[CONCURRENT EXECUTOR] "
            f"Dispatching {len(tasks)} task(s) "
            f"with max_concurrency="
            f"{self.max_concurrency}"
        )

        print(
            "[CONCURRENT EXECUTOR] "
            "Tasks="
            f"{[task.task_id for task in tasks]}"
        )

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

                results.append(
                    raw_result
                )

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
                        status=(
                            TaskExecutionStatus.CANCELLED
                        ),
                        error=(
                            "Task execution was cancelled."
                        ),
                        processing_results=[],
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
                        status=(
                            TaskExecutionStatus.FAILED
                        ),
                        error=str(raw_result),
                        processing_results=[],
                    )
                )

                continue

            raise TypeError(
                "Concurrent task executor received an "
                "unexpected result type: "
                f"{type(raw_result)!r}"
            )

        # ======================================================
        # TEMPORARY DEBUGGING: WAVE RESULT COLLECTION
        # ======================================================

        for result in results:

            debug_session.write(
                task_id=result.task_id,
                event="RECONCILED",
                message=(
                    "Task result collected by "
                    "ConcurrentTaskExecutor."
                ),
                status=result.status.value,
                processing_results=len(
                    result.processing_results
                ),
            )

        print()
        print(
            "[CONCURRENT EXECUTOR] "
            "All workers returned."
        )

        print(
            "[CONCURRENT EXECUTOR] "
            f"Results="
            f"{[(r.task_id, r.status.value) for r in results]}"
        )

        return results