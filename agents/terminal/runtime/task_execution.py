from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agents.terminal.task_executor.models import ExecutionWorkflow


class TaskExecutionStatus(StrEnum):
    """
    Runtime-local lifecycle of one task execution context.

    This is separate from TaskItemStatus.

    TaskItemStatus belongs to the TaskPlan.
    TaskExecutionStatus belongs to the scheduler/runtime execution.
    """

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskExecutionContext(BaseModel):
    """
    Isolated runtime context for one concurrently executing TaskItem.

    A TaskExecutionContext is the ownership boundary for all runtime
    execution state associated with a single task.

    It does not own TaskPlan lifecycle state. That remains the
    responsibility of TaskPlanManager.
    """

    execution_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this task execution instance.",
    )

    plan_id: str = Field(
        min_length=1,
        description="TaskPlan that owns this execution.",
    )

    task_id: str = Field(
        min_length=1,
        description="TaskItem being executed.",
    )

    status: TaskExecutionStatus = Field(
        default=TaskExecutionStatus.CREATED,
        description="Runtime-local execution lifecycle state.",
    )

    workflow: ExecutionWorkflow | None = Field(
        default=None,
        description="Workflow currently associated with this task execution.",
    )

    active_attempt_id: str | None = Field(
        default=None,
        description=(
            "ExecutionMemory attempt currently active for this task. "
            "This is task-scoped so concurrent tasks do not overwrite "
            "one another."
        ),
    )

    result: dict[str, Any] | None = Field(
        default=None,
        description="Task-local terminal execution result.",
    )

    error: str | None = Field(
        default=None,
        description="Task-local execution failure information.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional runtime metadata for this execution.",
    )