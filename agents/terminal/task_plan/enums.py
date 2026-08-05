from enum import StrEnum


class TaskPlanStatus(StrEnum):
    """
    Lifecycle state of a task plan.
    """

    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskItemStatus(StrEnum):
    """
    Lifecycle state of an individual task.
    """

    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
