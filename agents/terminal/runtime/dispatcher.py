from __future__ import annotations

from agents.terminal.runtime.modes import RuntimeMode
from agents.terminal.runtime.stages import RuntimeStage


_MODE_TO_STAGE = {
    RuntimeMode.INITIALIZING: RuntimeStage.PLANNER,

    RuntimeMode.PLANNING: RuntimeStage.PLANNER,

    RuntimeMode.EXECUTING: RuntimeStage.EXECUTOR,

    RuntimeMode.REVIEWING: RuntimeStage.CRITIC,

    RuntimeMode.FINISHED: RuntimeStage.TERMINATE,

    RuntimeMode.ERROR: RuntimeStage.ERROR,
}


class RuntimeDispatcher:
    """
    Maps runtime modes to subsystem stages.

    It performs no orchestration and no reasoning.
    """

    @classmethod
    def dispatch(
        cls,
        mode: RuntimeMode,
    ) -> RuntimeStage:

        try:
            return _MODE_TO_STAGE[mode]

        except KeyError as exc:
            raise RuntimeError(
                f"No dispatcher registered for runtime mode: "
                f"{mode.value}"
            ) from exc
            
    @classmethod
    def owns_stage(
        cls,
        *,
        mode: RuntimeMode,
        stage: RuntimeStage,
    ) -> bool:
        return cls.dispatch(mode) == stage