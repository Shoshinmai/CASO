from agents.terminal.critics.models import (
    CriticOutput,
)

from agents.terminal.runtime.events import (
    RuntimeEvent,
)

from agents.terminal.runtime.models import (
    RuntimeDecisionContext,
    RuntimeEvidence,
)


def critic_output_to_runtime_event(
    critic_output: CriticOutput,
) -> RuntimeEvent:
    """
    Convert a validated CriticOutput into the corresponding
    RuntimeEvent.

    This function performs no routing or orchestration.
    """

    decision = critic_output.decision

    try:
        return RuntimeEvent(decision.value)

    except ValueError as exc:
        raise ValueError(
            f"Critic decision '{decision.value}' does not "
            "have a corresponding RuntimeEvent."
        ) from exc


def critic_output_to_runtime_context(
    critic_output: CriticOutput,
) -> RuntimeDecisionContext:
    """
    Convert Critic-owned rationale and evidence into the
    runtime-neutral decision context.
    """

    return RuntimeDecisionContext(
        rationale=critic_output.rationale,
        evidence=[
            RuntimeEvidence(
                source=evidence.source,
                observation=evidence.observation,
            )
            for evidence in critic_output.evidence
        ],
    )


class CriticRuntimeEvent:
    """
    Runtime-facing representation of a Critic decision.

    The event identifies what happened.
    The decision context preserves why it happened.
    """

    def __init__(
        self,
        *,
        event: RuntimeEvent,
        context: RuntimeDecisionContext,
    ) -> None:
        self.event = event
        self.context = context


def build_critic_runtime_event(
    critic_output: CriticOutput,
) -> CriticRuntimeEvent:
    """
    Convert validated Critic output into the complete
    runtime-facing decision contract.
    """

    return CriticRuntimeEvent(
        event=critic_output_to_runtime_event(
            critic_output,
        ),
        context=critic_output_to_runtime_context(
            critic_output,
        ),
    )