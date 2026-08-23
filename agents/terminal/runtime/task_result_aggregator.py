from __future__ import annotations

from agents.terminal.runtime.task_execution import (
    TaskExecutionResult,
    TaskExecutionStatus,
)
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.task_plan.models import TaskPlan


class TaskResultAggregator:
    """
    Reconcile one completed execution wave with the authoritative
    TaskPlan.

    Workers never mutate TaskPlan directly.

    This class is the central mutation boundary after a concurrent
    execution wave has completed.
    """

    @staticmethod
    def aggregate(
        *,
        plan: TaskPlan,
        results: list[TaskExecutionResult],
    ) -> TaskPlan:
        """
        Apply all worker results to the TaskPlan.

        Results are processed in deterministic input order.

        Readiness is recalculated only after the entire wave has
        been reconciled.
        """

        seen_task_ids: set[str] = set()

        for result in results:

            # --------------------------------------------------
            # Duplicate protection
            # --------------------------------------------------

            if result.task_id in seen_task_ids:
                raise ValueError(
                    "Duplicate TaskExecutionResult received for "
                    f"task '{result.task_id}'."
                )

            seen_task_ids.add(
                result.task_id
            )

            task = TaskPlanManager.get_task(
                plan=plan,
                task_id=result.task_id,
            )

            # --------------------------------------------------
            # Successful task
            # --------------------------------------------------

            if result.status == TaskExecutionStatus.COMPLETED:

                TaskPlanManager.complete_task(
                    plan=plan,
                    task_id=task.task_id,
                )

                continue

            # --------------------------------------------------
            # Failed task
            # --------------------------------------------------

            if result.status == TaskExecutionStatus.FAILED:

                TaskPlanManager.fail_task(
                    plan=plan,
                    task_id=task.task_id,
                    reason=(
                        result.error
                        or "Task execution failed."
                    ),
                )

                continue

            # --------------------------------------------------
            # Cancelled task
            # --------------------------------------------------

            if result.status == TaskExecutionStatus.CANCELLED:

                TaskPlanManager.cancel_task(
                    plan=plan,
                    task_id=task.task_id,
                )

                continue

            raise ValueError(
                "TaskExecutionResult contains a non-terminal "
                f"status '{result.status}' for task "
                f"'{result.task_id}'."
            )

        # ------------------------------------------------------
        # Reconcile dependencies only after the complete wave.
        # ------------------------------------------------------

        TaskPlanManager.update_task_readiness(
            plan=plan,
        )

        return plan