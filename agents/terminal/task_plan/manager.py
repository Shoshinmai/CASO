from __future__ import annotations

from uuid import uuid4
from agents.terminal.task_plan.models import (
    TaskItemStatus,
    TaskPlanStatus,
    TaskPlan,
    TaskItem,
)


class TaskPlanManager:
    """
    Deterministic owner of TaskPlan state.

    This class is the only component allowed to mutate a TaskPlan.
    It performs no reasoning and contains no LLM logic.
    """

    from uuid import uuid4

    # ------------------------------------------------------------------
    # Plan Lifecycle
    # ------------------------------------------------------------------

    @staticmethod
    def create_plan(
        *,
        goal: str,
        tasks: list[TaskItem],
    ) -> TaskPlan:
        """
        Create a new task plan.

        This method only constructs the TaskPlan.
        It does not perform validation or determine execution order.
        """

        return TaskPlan(
            plan_id=str(uuid4()),
            goal=goal,
            status=TaskPlanStatus.CREATED,
            tasks=list(tasks),
        )

    @staticmethod
    def complete_plan(
        *,
        plan: TaskPlan,
    ) -> None:
        """
        Mark the task plan as completed.
        """

        plan.status = TaskPlanStatus.COMPLETED

    @staticmethod
    def fail_plan(
        *,
        plan: TaskPlan,
        reason: str | None = None,
    ) -> None:
        """
        Mark the task plan as failed.

        The failure reason is intentionally unused for now.
        It remains in the API for future plan diagnostics.
        """

        _ = reason

        plan.status = TaskPlanStatus.FAILED

    @staticmethod
    def cancel_plan(
        *,
        plan: TaskPlan,
    ) -> None:
        """
        Cancel the task plan.
        """

        plan.status = TaskPlanStatus.CANCELLED

    # ------------------------------------------------------------------
    # Task Lifecycle
    # ------------------------------------------------------------------

    @staticmethod
    def add_task(
        *,
        plan: TaskPlan,
        task: TaskItem,
    ) -> None:
        """
        Append a task to the end of the current plan.
        """

        plan.tasks.append(task)

    @staticmethod
    def insert_tasks(
        *,
        plan: TaskPlan,
        after_task_id: str | None,
        tasks: list[TaskItem],
    ) -> None:
        """
        Insert tasks into the plan.

        If after_task_id is None, insert at the beginning.
        """

        if after_task_id is None:
            plan.tasks[0:0] = tasks
            return

        for index, existing_task in enumerate(plan.tasks):
            if existing_task.task_id == after_task_id:
                plan.tasks[index + 1 : index + 1] = tasks
                return

        raise ValueError(f"Task '{after_task_id}' does not exist.")

    @staticmethod
    def remove_task(
        *,
        plan: TaskPlan,
        task_id: str,
    ) -> None:
        """
        Remove a task from the plan.
        """

        for index, task in enumerate(plan.tasks):
            if task.task_id == task_id:
                del plan.tasks[index]
                return

        raise ValueError(f"Task '{task_id}' does not exist.")

    @staticmethod
    def start_task(
        *,
        plan: TaskPlan,
        task_id: str,
    ) -> None:
        """
        Mark a task as in progress.
        """

        task = TaskPlanManager._find_task(
            plan=plan,
            task_id=task_id,
        )

        task.status = TaskItemStatus.IN_PROGRESS

    @staticmethod
    def complete_task(
        *,
        plan: TaskPlan,
        task_id: str,
    ) -> None:
        """
        Mark a task as completed.
        """

        task = TaskPlanManager._find_task(
            plan=plan,
            task_id=task_id,
        )

        task.status = TaskItemStatus.COMPLETED

    @staticmethod
    def block_task(
        *,
        plan: TaskPlan,
        task_id: str,
        blocker: str,
    ) -> None:
        """
        Mark a task as blocked.
        """

        task = TaskPlanManager._find_task(
            plan=plan,
            task_id=task_id,
        )

        task.status = TaskItemStatus.BLOCKED

        if blocker not in task.blockers:
            task.blockers.append(blocker)

    @staticmethod
    def fail_task(
        *,
        plan: TaskPlan,
        task_id: str,
        reason: str,
    ) -> None:
        """
        Mark a task as failed.
        """

        task = TaskPlanManager._find_task(
            plan=plan,
            task_id=task_id,
        )

        task.status = TaskItemStatus.FAILED

        if reason not in task.blockers:
            task.blockers.append(reason)

    @staticmethod
    def cancel_task(
        *,
        plan: TaskPlan,
        task_id: str,
    ) -> None:
        """
        Mark a task as cancelled.
        """

        task = TaskPlanManager._find_task(
            plan=plan,
            task_id=task_id,
        )

        task.status = TaskItemStatus.CANCELLED

    # ------------------------------------------------------------------
    # Rolling Plan
    # ------------------------------------------------------------------

    @staticmethod
    def get_ready_tasks(
        *,
        plan: TaskPlan,
    ) -> list[TaskItem]:
        """
        Return all tasks that are ready for execution.

        Tasks are returned in planner-defined order.
        """

        return [task for task in plan.tasks if task.status == TaskItemStatus.READY]

    @staticmethod
    def update_task_readiness(
        *,
        plan: TaskPlan,
    ) -> None:
        """
        Update task readiness based on dependency completion.

        Any PENDING task whose dependencies have all completed becomes READY.
        """

        completed_tasks = TaskPlanManager._completed_task_ids(plan)

        for task in plan.tasks:

            if task.status != TaskItemStatus.PENDING:
                continue

            if all(dependency in completed_tasks for dependency in task.dependencies):
                task.status = TaskItemStatus.READY

    @staticmethod
    def append_tasks(
        *,
        plan: TaskPlan,
        tasks: list[TaskItem],
    ) -> None:
        """
        Append new tasks to the end of the current task plan.

        This is primarily used when the planner expands the
        rolling task plan during execution.
        """

        plan.tasks.extend(tasks)

    @staticmethod
    def replace_remaining_tasks(
        *,
        plan: TaskPlan,
        tasks: list[TaskItem],
    ) -> None:
        """
        Replace all incomplete tasks with a new set of tasks.

        Completed tasks are preserved to maintain execution history.
        This is primarily used after a replanning operation.
        """

        completed_tasks = [
            task
            for task in plan.tasks
            if task.status == TaskItemStatus.COMPLETED
        ]

        plan.tasks = completed_tasks + list(tasks)

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_task(
        *,
        plan: TaskPlan,
        task_id: str,
    ) -> TaskItem:
        """
        Return the task with the given ID.

        Raises:
            ValueError: If the task does not exist.
        """

        for task in plan.tasks:
            if task.task_id == task_id:
                return task

        raise ValueError(f"Task '{task_id}' does not exist.")

    @staticmethod
    def _completed_task_ids(
        plan: TaskPlan,
    ) -> set[str]:

        return {
            task.task_id
            for task in plan.tasks
            if task.status == TaskItemStatus.COMPLETED
        }
