from typing import Any

from agents.terminal.critics.models import CriticContext

# Use the EXISTING utilities/APIs already implemented
# in your project for these sections.
from agents.terminal.utils.memory_formatter import (
    format_active_memory,
    format_artifact_catalog,
    format_execution_summary,
)

from agents.terminal.task_plan.manager import (
    TaskPlanManager,
)


def build_critic_context(
    state: dict[str, Any],
) -> CriticContext:
    """
    Build the complete context supplied to the Critic.

    This function only composes existing context providers.
    It does not implement formatting or TaskPlan logic.
    """

    task_plan = state["task_plan"]

    current_task = TaskPlanManager.get_current_task(
        plan=task_plan,
    )

    if current_task is None:
        raise ValueError(
            "Cannot build CriticContext without a current task."
        )

    return CriticContext(
        overall_goal=task_plan.goal,

        current_objective=current_task.objective,

        remaining_objectives=(
            TaskPlanManager.format_remaining_tasks(
                plan=task_plan,
                exclude_task_id=current_task.task_id,
            )
        ),

        execution_summary=(
            format_execution_summary(
                state["execution_memory"],
            )
        ),

        active_memory=(
            format_active_memory(
                active_memory=state["active_memory"],
            )
        ),

        artifact_catalog=(
            format_artifact_catalog(
                state.get("artifact_references", []),
            )
        ),
    )