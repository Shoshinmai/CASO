from __future__ import annotations

from agents.terminal.runtime.concurrent_task_executor import (
    ConcurrentTaskExecutor,
)
from agents.terminal.runtime.task_result_reconciler import (
    TaskResultReconciler,
)
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.task_plan.models import TaskPlan


class TaskExecutionCoordinator:
    """
    Orchestrate dependency-aware concurrent execution waves.

    Responsibilities:
    - discover the current READY tasks
    - start one execution wave
    - run the wave concurrently
    - reconcile all results centrally
    - continue with the next READY wave

    This component owns orchestration only.

    It does not:
    - execute individual tasks
    - reason about task objectives
    - mutate TaskItems directly
    - perform LLM calls
    """

    def __init__(
        self,
        *,
        executor: ConcurrentTaskExecutor,
    ) -> None:
        self.executor = executor

    async def execute_plan(
        self,
        *,
        plan: TaskPlan,
        state: dict,
    ) -> TaskPlan:
        """
        Execute the task plan wave-by-wave until completion or
        until no further executable work exists.
        """

        # ------------------------------------------------------
        # Establish initial readiness.
        # ------------------------------------------------------

        TaskPlanManager.update_task_readiness(
            plan=plan,
        )

        while True:

            # --------------------------------------------------
            # Plan already completed.
            # --------------------------------------------------

            if TaskPlanManager.is_plan_complete(
                plan=plan,
            ):
                break

            # --------------------------------------------------
            # Select the current execution wave.
            #
            # The ConcurrentTaskExecutor itself enforces the
            # configured concurrency limit.
            # --------------------------------------------------

            ready_tasks = TaskPlanManager.get_ready_tasks(
                plan=plan,
            )

            # --------------------------------------------------
            # No READY work.
            #
            # This means either:
            # - tasks are still being executed elsewhere, or
            # - all remaining work is blocked/terminal.
            #
            # In this coordinator, there are no other running
            # workers because each wave is fully awaited, so
            # there is no valid next wave.
            # --------------------------------------------------

            if not ready_tasks:

                blocked_tasks = (
                    TaskPlanManager.get_blocked_tasks(
                        plan=plan,
                    )
                )

                if blocked_tasks:
                    break

                # No READY tasks and no blocked tasks means the
                # plan cannot currently make progress.
                break

            # --------------------------------------------------
            # Admit the entire current READY wave.
            #
            # This is the only place we transition READY →
            # IN_PROGRESS before worker execution begins.
            # --------------------------------------------------

            execution_wave = (
                TaskPlanManager.start_ready_tasks(
                    plan=plan,
                    limit=len(ready_tasks),
                )
            )

            if not execution_wave:
                break

            # --------------------------------------------------
            # Execute the entire wave concurrently.
            # --------------------------------------------------

            results = await self.executor.execute(
                plan_id=plan.plan_id,
                tasks=execution_wave,
                state=state,
            )

            # --------------------------------------------------
            # Reconcile all results only after the complete wave
            # has finished.
            # --------------------------------------------------

            TaskResultReconciler.reconcile(
                plan=plan,
                results=results,
            )

            # --------------------------------------------------
            # The reconciler has updated readiness.
            #
            # Loop back and compute the next wave.
            # --------------------------------------------------

        return plan