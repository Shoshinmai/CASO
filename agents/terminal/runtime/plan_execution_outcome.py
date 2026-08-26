from dataclasses import dataclass, field
from enum import Enum


class PlanExecutionCondition(str, Enum):
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PlanExecutionOutcome:
    plan_id: str
    condition: PlanExecutionCondition

    completed_task_ids: list[str] = field(
        default_factory=list,
    )

    failed_task_ids: list[str] = field(
        default_factory=list,
    )

    blocked_task_ids: list[str] = field(
        default_factory=list,
    )

    cancelled_task_ids: list[str] = field(
        default_factory=list,
    )

    task_results: dict = field(
        default_factory=dict,
    )