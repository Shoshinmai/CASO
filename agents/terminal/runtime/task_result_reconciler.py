from __future__ import annotations

from agents.terminal.runtime.task_execution import (
    TaskExecutionResult,
    TaskExecutionStatus,
)
from agents.terminal.task_plan.manager import (
    TaskPlanManager,
)
from agents.terminal.task_plan.models import (
    TaskPlan,
)


class TaskResultReconciler:
    """
    Reconcile terminal task execution results into the authoritative
    TaskPlan.

    This is the boundary between task-local worker execution and
    central TaskPlan lifecycle state.

    Workers never mutate the TaskPlan directly. They return
    TaskExecutionResult objects. This reconciler applies those
    results centrally after an execution wave has finished.
    """

    @staticmethod
    def reconcile(
        *,
        plan: TaskPlan,
        results: list[TaskExecutionResult],
    ) -> TaskPlan:
        """
        Reconcile one completed execution wave.

        The entire result wave is first applied to the authoritative
        task states. Dependency readiness is updated only after all
        results have been reconciled.

        Returns the same mutated TaskPlan instance.
        """

        # ------------------------------------------------------
        # Validate that all results belong to this plan.
        # ------------------------------------------------------

        for result in results:

            if result.plan_id != plan.plan_id:
                raise ValueError(
                    "Cannot reconcile a result belonging to a "
                    f"different plan. Expected '{plan.plan_id}', "
                    f"received '{result.plan_id}'."
                )

        # ------------------------------------------------------
        # Apply all terminal execution outcomes.
        #
        # Do not update dependency readiness inside this loop.
        # A whole execution wave must be reconciled first.
        # ------------------------------------------------------

        for result in results:

            if result.status == TaskExecutionStatus.COMPLETED:

                TaskPlanManager.complete_task(
                    plan=plan,
                    task_id=result.task_id,
                )

                continue

            if result.status == TaskExecutionStatus.FAILED:

                TaskPlanManager.fail_task(
                    plan=plan,
                    task_id=result.task_id,
                    reason=(
                        result.error
                        or "Task execution failed."
                    ),
                )

                continue

            if result.status == TaskExecutionStatus.CANCELLED:

                TaskPlanManager.cancel_task(
                    plan=plan,
                    task_id=result.task_id,
                )

                continue

            raise ValueError(
                "Cannot reconcile non-terminal task execution "
                f"status '{result.status}'."
            )

        # ------------------------------------------------------
        # Recompute readiness after the entire wave is applied.
        # ------------------------------------------------------

        TaskPlanManager.update_task_readiness(
            plan=plan,
        )

        # ------------------------------------------------------
        # Mark tasks blocked by failed/cancelled dependencies.
        # ------------------------------------------------------

        blocked_tasks = (
            TaskPlanManager.get_blocked_tasks(
                plan=plan,
            )
        )

        for task in blocked_tasks:

            TaskPlanManager.block_task(
                plan=plan,
                task_id=task.task_id,
                blocker=(
                    "A required dependency did not complete "
                    "successfully."
                ),
            )

        # ------------------------------------------------------
        # Recompute plan terminal state.
        #
        # For now, only the deterministic all-completed condition
        # completes the plan.
        # ------------------------------------------------------

        if TaskPlanManager.is_plan_complete(
            plan=plan,
        ):
            TaskPlanManager.complete_plan(
                plan=plan,
            )

        return plan