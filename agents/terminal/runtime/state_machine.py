from __future__ import annotations

from dataclasses import dataclass

from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.modes import RuntimeMode


@dataclass(frozen=True, slots=True)
class Transition:
    """
    A deterministic runtime transition.

    Represents:
        Current RuntimeMode
            +
        RuntimeEvent
            ->
        Next RuntimeMode
    """

    mode: RuntimeMode
    event: RuntimeEvent


# ---------------------------------------------------------------------
# Runtime Transition Table
# ---------------------------------------------------------------------

_TRANSITIONS: dict[Transition, RuntimeMode] = {
    # ================================================================
    # Planning
    # ================================================================

    # Planner successfully created (or updated) a plan.
    Transition(
        RuntimeMode.PLANNING,
        RuntimeEvent.PLAN_CREATED,
    ): RuntimeMode.EXECUTING,

    Transition(
        RuntimeMode.PLANNING,
        RuntimeEvent.PLAN_UPDATED,
    ): RuntimeMode.EXECUTING,

    # Planner could not create a valid plan.
    Transition(
        RuntimeMode.PLANNING,
        RuntimeEvent.PLAN_FAILED,
    ): RuntimeMode.ERROR,

    Transition(
        RuntimeMode.PLANNING,
        RuntimeEvent.PLAN_CANCELLED,
    ): RuntimeMode.FINISHED,

    # ================================================================
    # Execution
    # ================================================================

    # Regardless of success/failure, execution must be reviewed.
    Transition(
        RuntimeMode.EXECUTING,
        RuntimeEvent.EXECUTION_COMPLETED,
    ): RuntimeMode.REVIEWING,

    Transition(
        RuntimeMode.EXECUTING,
        RuntimeEvent.EXECUTION_FAILED,
    ): RuntimeMode.REVIEWING,

    # ================================================================
    # Review
    # ================================================================

    # Critic decided the current objective is not finished.
    Transition(
        RuntimeMode.REVIEWING,
        RuntimeEvent.CONTINUE_TASK,
    ): RuntimeMode.EXECUTING,

    # Retry same objective.
    Transition(
        RuntimeMode.REVIEWING,
        RuntimeEvent.RETRY_TASK,
    ): RuntimeMode.EXECUTING,

    # Current objective completed.
    #
    # The dispatcher / kernel will ask the TaskPlanManager
    # whether another objective exists.
    Transition(
        RuntimeMode.REVIEWING,
        RuntimeEvent.TASK_COMPLETED,
    ): RuntimeMode.EXECUTING,

    # Strategy no longer valid.
    Transition(
        RuntimeMode.REVIEWING,
        RuntimeEvent.REPLAN_REQUIRED,
    ): RuntimeMode.PLANNING,

    # Whole user goal completed.
    Transition(
        RuntimeMode.REVIEWING,
        RuntimeEvent.GOAL_COMPLETED,
    ): RuntimeMode.FINISHED,
}

class InvalidRuntimeTransition(RuntimeError):
    """Raised when an invalid runtime transition is requested."""


class RuntimeStateMachine:
    """
    Deterministic runtime state machine.

    Responsibilities:
        - Validate runtime transitions.
        - Determine the next runtime mode.

    Responsibilities it does NOT have:
        - Execute nodes
        - Invoke the LLM
        - Mutate runtime state
        - Know about LangGraph
    """

    @classmethod
    def transition(
        cls,
        *,
        current_mode: RuntimeMode,
        event: RuntimeEvent,
    ) -> RuntimeMode:
        transition = Transition(
            mode=current_mode,
            event=event,
        )

        try:
            return _TRANSITIONS[transition]

        except KeyError as exc:
            raise InvalidRuntimeTransition(
                f"Invalid runtime transition: "
                f"{current_mode.value} --({event.value})-> ?"
            ) from exc

    @classmethod
    def can_transition(
        cls,
        *,
        current_mode: RuntimeMode,
        event: RuntimeEvent,
    ) -> bool:
        return Transition(
            current_mode,
            event,
        ) in _TRANSITIONS

    @classmethod
    def valid_events(
        cls,
        mode: RuntimeMode,
    ) -> tuple[RuntimeEvent, ...]:
        return tuple(
            transition.event
            for transition in _TRANSITIONS
            if transition.mode == mode
        )