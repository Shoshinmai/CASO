from __future__ import annotations

from agents.terminal.runtime.dispatcher import RuntimeDispatcher
from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.models import RuntimeState
from agents.terminal.runtime.modes import RuntimeMode
from agents.terminal.runtime.stages import RuntimeStage
from agents.terminal.runtime.state_machine import RuntimeStateMachine


class RuntimeKernel:
    """
    Public façade for the Terminal Agent Runtime.

    Responsibilities
    ----------------
    - Own RuntimeState mutations.
    - Validate runtime transitions.
    - Determine the next runtime stage.

    It intentionally knows nothing about:
        • LangGraph
        • Planner implementation
        • Executor implementation
        • Critic implementation
        • Tool execution
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def handle_event(
        cls,
        *,
        runtime_state: RuntimeState,
        event: RuntimeEvent,
    ) -> RuntimeStage:
        """
        Process a runtime event and return the next runtime stage.
        """

        next_mode = RuntimeStateMachine.transition(
            current_mode=runtime_state.mode,
            event=event,
        )

        cls._update_runtime_state(
            runtime_state=runtime_state,
            next_mode=next_mode,
            event=event,
        )

        return RuntimeDispatcher.dispatch(next_mode)

    @classmethod
    def current_stage(
        cls,
        *,
        runtime_state: RuntimeState,
    ) -> RuntimeStage:
        """
        Return the subsystem that currently owns execution.
        """

        return RuntimeDispatcher.dispatch(runtime_state.mode)

    @classmethod
    def reset(
        cls,
        *,
        runtime_state: RuntimeState,
    ) -> None:
        """
        Reset the runtime to its initial state.
        """

        runtime_state.mode = RuntimeMode.INITIALIZING
        runtime_state.last_event = None
        runtime_state.iteration = 0

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _update_runtime_state(
        *,
        runtime_state: RuntimeState,
        next_mode: RuntimeMode,
        event: RuntimeEvent,
    ) -> None:
        """
        Apply deterministic RuntimeState mutations.

        This is the only place where RuntimeState is mutated.
        """

        runtime_state.mode = next_mode
        runtime_state.last_event = event
        runtime_state.iteration += 1
