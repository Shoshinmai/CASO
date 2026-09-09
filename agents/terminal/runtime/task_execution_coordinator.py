from __future__ import annotations

from dataclasses import dataclass, field

from agents.terminal.runtime.concurrent_task_executor import (
    ConcurrentTaskExecutor,
)
from agents.terminal.runtime.task_execution import (
    TaskExecutionResult,
)
from agents.terminal.runtime.task_result_reconciler import (
    TaskResultReconciler,
)
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.task_plan.models import TaskPlan


@dataclass
class CoordinatedPlanExecution:
    """
    Terminal result of the coordinator's execution loop.

    The coordinator owns execution orchestration and preserves the
    task-local terminal results produced across all execution waves.
    """

    plan: TaskPlan

    task_results: list[TaskExecutionResult] = field(
        default_factory=list,
    )


class TaskExecutionCoordinator:
    """
    Orchestrate dependency-aware concurrent execution waves.

    Responsibilities:
    - discover the current READY tasks
    - start one execution wave
    - run the wave concurrently
    - reconcile all results centrally
    - preserve results across execution waves
    - continue with the next READY wave

    This component owns orchestration only.

    It does not:
    - execute individual tasks
    - reason about task objectives
    - mutate TaskItems directly
    - perform LLM calls
    - make semantic critic decisions
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
    ) -> CoordinatedPlanExecution:
        """
        Execute the task plan wave-by-wave until completion or
        until no further executable work exists.

        Returns the authoritative TaskPlan together with all
        terminal TaskExecutionResults produced during this
        coordinator run.
        """

        all_task_results: list[
            TaskExecutionResult
        ] = []

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
                print(
                    "\n[COORDINATOR] "
                    "Plan already complete."
                )
                break

            # --------------------------------------------------
            # Select the current execution wave.
            #
            # The ConcurrentTaskExecutor itself enforces the
            # configured concurrency limit.
            # --------------------------------------------------

            ready_tasks = (
                TaskPlanManager.get_ready_tasks(
                    plan=plan,
                )
            )

            print(
                "\n[COORDINATOR] "
                f"READY tasks: "
                f"{[task.task_id for task in ready_tasks]}"
            )

            # --------------------------------------------------
            # No READY work.
            # --------------------------------------------------

            if not ready_tasks:

                print(
                    "[COORDINATOR] "
                    "No READY tasks remain."
                )

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

                print(
                    "[COORDINATOR] "
                    "No tasks were admitted into the wave."
                )

                break

            print(
                "\n[COORDINATOR] "
                f"Starting execution wave | "
                f"tasks="
                f"{[task.task_id for task in execution_wave]}"
            )

            # --------------------------------------------------
            # Execute the entire wave concurrently.
            # --------------------------------------------------

            results = await self.executor.execute(
                plan_id=plan.plan_id,
                tasks=execution_wave,
                state=state,
            )

            # --------------------------------------------------
            # Preserve terminal task-local evidence from this
            # wave before moving to the next one.
            # --------------------------------------------------

            all_task_results.extend(
                results,
            )

            print(
                "\n[COORDINATOR] "
                f"Wave execution complete | "
                f"results="
                f"{[result.task_id for result in results]}"
            )

            # --------------------------------------------------
            # Reconcile all results only after the complete wave
            # has finished.
            #
            # D.7.4:
            #
            # The reconciler now returns an explicit summary of
            # the central state transition caused by this wave.
            # --------------------------------------------------

            reconciliation = (
                TaskResultReconciler.reconcile(
                    plan=plan,
                    results=results,
                    state=state,
                )
            )

            print(
                "\n[COORDINATOR] "
                "Wave reconciliation complete."
            )

            print(
                "[COORDINATOR] "
                f"Reconciled: "
                f"{reconciliation.reconciled_task_ids}"
            )

            print(
                "[COORDINATOR] "
                f"New READY: "
                f"{reconciliation.newly_ready_task_ids}"
            )

            print(
                "[COORDINATOR] "
                f"Blocked: "
                f"{reconciliation.blocked_task_ids}"
            )

            print(
                "[COORDINATOR] "
                f"Merged attempts: "
                f"{reconciliation.merged_attempt_ids}"
            )

            print(
                "[COORDINATOR] "
                f"Persisted artifacts: "
                f"{reconciliation.persisted_artifact_ids}"
            )

            # --------------------------------------------------
            # The reconciler has updated readiness.
            #
            # Loop back and compute the next wave.
            # --------------------------------------------------

        return CoordinatedPlanExecution(
            plan=plan,
            task_results=all_task_results,
        )