from __future__ import annotations

from typing import Any

from agents.terminal.critics.models import CriticContext
from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.plan_execution_outcome import (
    PlanExecutionOutcome,
)
from agents.terminal.state import TerminalState
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.task_plan.models import TaskPlan
from agents.terminal.utils.memory_formatter import (
    format_active_memory,
    format_artifact_catalog,
    format_execution_summary,
    format_task_plan,
)


def build_critic_context(
    state: dict[str, Any] | TerminalState,
) -> CriticContext:
    """
    Build the complete context supplied to the Critic.

    The Critic receives a relevant, formatted view of the current
    execution situation rather than the raw runtime state.

    The builder supports both:

    1. The existing single-task runtime path.
    2. The new concurrent plan-level execution path.

    This function does not:
        - perform Critic reasoning,
        - modify the TaskPlan,
        - modify the ExecutionWorkflow,
        - execute tools,
        - perform runtime routing.
    """

    task_plan = state.get(
        "task_plan",
    )

    if task_plan is None:
        raise ValueError(
            "Cannot build CriticContext without a TaskPlan."
        )

    plan_execution_outcome = state.get(
        "plan_execution_outcome",
    )

    # ----------------------------------------------------------
    # Shared context
    # ----------------------------------------------------------

    overall_goal = task_plan.goal

    task_plan_summary = format_task_plan(
        task_plan,
    )

    execution_summary = _build_execution_summary(
        state,
    )

    active_memory = format_active_memory(
        active_memory=state["active_memory"],
    )

    artifact_catalog = format_artifact_catalog(
        state.get(
            "artifact_references",
            [],
        ),
    )

    # ----------------------------------------------------------
    # Concurrent plan-level review
    # ----------------------------------------------------------

    if plan_execution_outcome is not None:

        return _build_concurrent_critic_context(
            task_plan=task_plan,
            outcome=plan_execution_outcome,
            execution_summary=execution_summary,
            active_memory=active_memory,
            artifact_catalog=artifact_catalog,
            task_plan_summary=task_plan_summary,
        )

    # ----------------------------------------------------------
    # Existing single-task review path
    # ----------------------------------------------------------

    runtime_state = state.get(
        "runtime_state",
    )

    current_task = TaskPlanManager.get_in_progress_task(
        plan=task_plan,
    )

    # ----------------------------------------------------------
    # Plan exhaustion review
    # ----------------------------------------------------------

    if (
        runtime_state is not None
        and runtime_state.last_event
        == RuntimeEvent.PLAN_EXHAUSTED
    ):

        return CriticContext(
            overall_goal=overall_goal,

            task_plan_summary=task_plan_summary,

            plan_execution_outcome=(
                "The rolling TaskPlan has been exhausted. "
                "No further task execution remains."
            ),

            current_objective=(
                "All planned objectives have been completed. "
                "Determine whether the overall user goal has "
                "actually been achieved."
            ),

            remaining_objectives=(
                "No remaining objectives."
            ),

            execution_summary=execution_summary,

            active_memory=active_memory,

            artifact_catalog=artifact_catalog,
        )

    if current_task is None:
        raise ValueError(
            "Cannot build CriticContext because the TaskPlan "
            "has no IN_PROGRESS task."
        )

    return CriticContext(
        overall_goal=overall_goal,

        task_plan_summary=task_plan_summary,

        plan_execution_outcome=(
            "The runtime is reviewing the current task "
            "using the existing single-task execution path."
        ),

        current_objective=current_task.objective,

        remaining_objectives=_build_remaining_objectives(
            task_plan=task_plan,
            current_task_id=current_task.task_id,
        ),

        execution_summary=execution_summary,

        active_memory=active_memory,

        artifact_catalog=artifact_catalog,
    )


def _build_concurrent_critic_context(
    *,
    task_plan: TaskPlan,
    outcome: PlanExecutionOutcome,
    execution_summary: str,
    active_memory: str,
    artifact_catalog: str,
    task_plan_summary: str,
) -> CriticContext:
    """
    Build CriticContext for a completed concurrent execution
    boundary.

    The Critic receives the whole plan-level situation rather than
    a singular current task.
    """

    return CriticContext(
        overall_goal=task_plan.goal,

        task_plan_summary=task_plan_summary,

        plan_execution_outcome=(
            _format_plan_execution_outcome(
                outcome,
            )
        ),

        current_objective=(
            _build_concurrent_execution_situation(
                outcome,
            )
        ),

        remaining_objectives=(
            _build_remaining_objectives_for_plan(
                task_plan,
            )
        ),

        execution_summary=execution_summary,

        active_memory=active_memory,

        artifact_catalog=artifact_catalog,
    )


def _build_concurrent_execution_situation(
    outcome: PlanExecutionOutcome,
) -> str:
    """
    Build a concise semantic description of the current
    concurrent execution situation.

    This preserves the existing `current_objective` field for
    compatibility while removing the assumption that there is
    exactly one current task.
    """

    condition = outcome.condition.value

    if outcome.failed_task_ids:
        return (
            "Concurrent execution reached a stable boundary "
            f"with condition '{condition}'. "
            "One or more tasks failed and may require "
            "semantic recovery."
        )

    if outcome.blocked_task_ids:
        return (
            "Concurrent execution reached a stable boundary "
            f"with condition '{condition}'. "
            "One or more tasks are blocked by dependency "
            "state."
        )

    if outcome.cancelled_task_ids:
        return (
            "Concurrent execution reached a stable boundary "
            f"with condition '{condition}'. "
            "One or more tasks were cancelled."
        )

    if outcome.condition.value == "completed":
        return (
            "Concurrent execution completed all planned tasks. "
            "Determine whether the overall user goal has been "
            "achieved."
        )

    return (
        "Concurrent execution reached a stable plan-level "
        f"boundary with condition '{condition}'."
    )


def _format_plan_execution_outcome(
    outcome: PlanExecutionOutcome,
) -> str:
    """
    Format the structured concurrent execution outcome for the
    Critic prompt.

    No semantic interpretation is performed here.
    """

    lines = [
        f"Condition: {outcome.condition.value}",
        "",
        "Completed Tasks:",
    ]

    if outcome.completed_task_ids:
        lines.extend(
            f"- {task_id}"
            for task_id in outcome.completed_task_ids
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Failed Tasks:",
        ]
    )

    if outcome.failed_task_ids:
        lines.extend(
            f"- {task_id}"
            for task_id in outcome.failed_task_ids
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Blocked Tasks:",
        ]
    )

    if outcome.blocked_task_ids:
        lines.extend(
            f"- {task_id}"
            for task_id in outcome.blocked_task_ids
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Cancelled Tasks:",
        ]
    )

    if outcome.cancelled_task_ids:
        lines.extend(
            f"- {task_id}"
            for task_id in outcome.cancelled_task_ids
        )
    else:
        lines.append("- None")

    if outcome.task_results:
        lines.extend(
            [
                "",
                "Task Execution Results:",
            ]
        )

        for task_id, result in outcome.task_results.items():

            lines.append(
                f"- {task_id}: "
                f"{result.status.value}"
            )

            if result.error:
                lines.append(
                    f"  Error: {result.error}"
                )

            if result.result is not None:
                lines.append(
                    f"  Result: {result.result}"
                )

    return "\n".join(lines)


def _build_remaining_objectives_for_plan(
    task_plan: TaskPlan,
) -> str:
    """
    Build the set of objectives that are not completed.

    Unlike the legacy single-task path, this includes the entire
    relevant remainder of the rolling plan.
    """

    remaining_tasks = [
        task
        for task in task_plan.tasks
        if task.status.value
        not in {
            "completed",
            "cancelled",
        }
    ]

    if not remaining_tasks:
        return "No remaining objectives."

    lines = []

    for index, task in enumerate(
        remaining_tasks,
        start=1,
    ):
        lines.append(
            f"{index}. "
            f"[{task.status.value}] "
            f"{task.objective}"
        )

        if task.dependencies:
            lines.append(
                "   depends on: "
                + ", ".join(task.dependencies)
            )

    return "\n".join(lines)


def _build_remaining_objectives(
    *,
    task_plan: Any | TaskPlan,
    current_task_id: str,
) -> str:
    """
    Build a compact Critic-facing representation of the
    objectives that remain in the TaskPlan.

    Preserved for the existing single-task execution path.
    """

    remaining_tasks = [
        task
        for task in task_plan.tasks
        if (
            task.task_id != current_task_id
            and task.status.value
            not in {
                "completed",
                "cancelled",
            }
        )
    ]

    if not remaining_tasks:
        return "No remaining objectives."

    lines = []

    for index, task in enumerate(
        remaining_tasks,
        start=1,
    ):
        lines.append(
            f"{index}. {task.objective}"
        )

    return "\n".join(lines)


def _build_execution_summary(
    state: dict[str, Any] | TerminalState,
) -> str:
    """
    Build the Critic-facing execution summary.

    Existing execution memory remains the primary source of
    execution history.

    The current ExecutionWorkflow is appended only when the
    legacy single-workflow path is active.
    """

    summary = format_execution_summary(
        state["execution_memory"],
    )

    workflow = state.get(
        "execution_workflow",
    )

    if workflow is None:
        return summary

    workflow_lines = [
        "",
        "CURRENT EXECUTION WORKFLOW",
        "---------------------------",
        f"Workflow ID: {workflow.workflow_id}",
        f"Workflow Objective: {workflow.objective}",
        f"Workflow Strategy: {workflow.execution_strategy}",
        f"Workflow Status: {workflow.status.value}",
    ]

    if workflow.steps:

        workflow_lines.append("")
        workflow_lines.append(
            "Workflow Steps:"
        )

        for index, step in enumerate(
            workflow.steps,
            start=1,
        ):

            workflow_lines.append(
                f"{index}. {step.description}"
            )

            workflow_lines.append(
                f"   Capability: {step.capability}"
            )

            workflow_lines.append(
                f"   Status: {step.status.value}"
            )

    return (
        summary
        + "\n"
        + "\n".join(workflow_lines)
    )