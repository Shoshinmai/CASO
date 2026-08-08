from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CriticDecision(StrEnum):
    """
    Decision produced by the Critic after evaluating
    the current task objective.
    """

    CONTINUE_TASK = "continue_task"

    TASK_COMPLETED = "task_completed"

    RETRY_TASK = "retry_task"

    PLAN_UPDATE_REQUIRED = "plan_update_required"

    REPLAN_REQUIRED = "replan_required"

    GOAL_COMPLETED = "goal_completed"


class CriticEvidence(BaseModel):
    """
    A factual piece of evidence supporting the Critic's decision.
    """

    source: str = Field(
        min_length=1,
        description=(
            "Source of the evidence, such as execution memory, "
            "active task memory, artifact catalog, or workflow result."
        ),
    )

    observation: str = Field(
        min_length=1,
        description="Factual observation supporting the decision.",
    )


class CriticOutput(BaseModel):
    """
    Structured semantic evaluation produced by the Critic.

    The Critic evaluates the current objective and recommends
    what the Runtime should do next.

    It does not perform the recommended action.
    """

    decision: CriticDecision = Field(
        description="Decision produced by the Critic.",
    )

    rationale: str = Field(
        min_length=1,
        description=(
            "Explanation of why this decision is appropriate "
            "given the available evidence."
        ),
    )

    evidence: list[CriticEvidence] = Field(
        min_length=1,
        description=(
            "Factual evidence supporting the Critic's decision."
        ),
    )