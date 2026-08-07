from typing import Any

from agents.terminal.task_plan.models import TaskItemStatus
from agents.terminal.utils.memory_formatter import (
    format_active_memory,
    format_execution_summary,
    format_task_plan,
)


def build_planner_context(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the complete context consumed by the strategic planner.

    This is the single source of truth for every placeholder used by
    TERMINAL_PLANNER_PROMPT.
    """

    return {
        "goal": _build_goal(state),
        "active_memory": _build_active_memory(state),
        "task_plan": _build_task_plan(state),
        "execution_summary": _build_execution_summary(state),
    }


# ----------------------------------------------------------------------
# Individual Builders
# ----------------------------------------------------------------------


def _build_goal(state: dict[str, Any]) -> str:
    return state.get("task").goal


def _build_active_memory(state: dict[str, Any]) -> str:
    memory = format_active_memory(
        active_memory=state["active_memory"],
    )

    return memory if memory else "No task knowledge available."


def _build_task_plan(state: dict[str, Any]) -> str:
    task_plan = state.get("task_plan")

    if task_plan is None:
        return "No task plan exists yet."

    return format_task_plan(task_plan)


def _build_execution_summary(state: dict[str, Any]) -> str:
    execution_memory = state.get("execution_memory")

    if execution_memory is None:
        return "No execution history available."

    return format_execution_summary(execution_memory)