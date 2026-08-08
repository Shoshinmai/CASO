from __future__ import annotations

from typing import Any

from agents.terminal.models import ActiveTaskMemory, ArtifactReference, ExecutionMemory
from agents.terminal.task_plan.models import TaskPlan
from agents.terminal.utils.memory_formatter import (
    format_active_memory,
    format_artifact_catalog,
    format_execution_summary,
)
from agents.terminal.task_executor.models import ExecutionContext
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.utils.tool_prompt_builder import build_capability_prompt


def build_execution_context(
    state: dict[str, Any],
) -> ExecutionContext:
    """
    Build the structured context consumed by the Task Executor.
    """

    task_plan = state["task_plan"]

    return ExecutionContext(
        objective=_build_objective(task_plan),
        active_memory=_build_active_memory(
            state["active_memory"],
        ),
        execution_summary=_build_execution_summary(
            state["execution_memory"],
        ),
        artifact_catalog=_build_artifact_catalog(
            state["artifact_references"],
        ),
        capabilities=_build_capabilities(
            state["capabilities"],
        ),
    )

def _build_objective(
    task_plan: TaskPlan,
) -> str:
    """
    Return the objective of the current executable task.
    """

    current_task = TaskPlanManager.get_current_task(
        task_plan,
    )

    if current_task is None:
        return "No executable task."

    return current_task.objective

def _build_active_memory(
    active_memory: ActiveTaskMemory,
) -> str:
    return format_active_memory(active_memory)

def _build_execution_summary(
    execution_memory: ExecutionMemory,
) -> str:
    return format_execution_summary(
        execution_memory,
    )
    
def _build_artifact_catalog(
    artifact_references: list[ArtifactReference],
) -> str:
    return format_artifact_catalog(
        artifact_references,
    )

def _build_capabilities(
    capabilities: list,
) -> str:
    return build_capability_prompt(
        capabilities,
    )