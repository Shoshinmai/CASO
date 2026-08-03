from typing import Any

from agents.terminal.utils.memory_formatter import format_active_memory


def build_planner_context(
    state: dict[str, Any],
    capability_prompt: str,
) -> dict[str, Any]:
    """
    Build the complete context consumed by the planner prompt.

    This is the single source of truth for every placeholder used by
    TERMINAL_PLANNER_PROMPT.
    """

    return {
        "goal": _build_goal(state),
        "active_memory": _build_active_memory(state),
        "artifact_context": _build_artifact_context(state),
        "validation_error": _build_validation_error(state),
        "safety_reason": _build_safety_reason(state),
        "capabilities": capability_prompt,
    }


def _build_goal(state: dict[str, Any]) -> str:
    return state["task"].goal


def _build_active_memory(state: dict[str, Any]) -> str:
    memory = format_active_memory(
        active_memory=state["active_memory"],
    )

    return memory if memory else "No task knowledge available."


def _build_artifact_context(state: dict[str, Any]) -> str:
    artifacts = state.get("artifact_references", [])

    if not artifacts:
        return "None"

    return "\n".join(
        f"- {artifact.identifier}"
        for artifact in artifacts
    )


def _build_validation_error(state: dict[str, Any]) -> str:
    return state.get("validation_error") or "None"


def _build_safety_reason(state: dict[str, Any]) -> str:
    return state.get("safety_reason") or "None"