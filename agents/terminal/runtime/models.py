from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .events import RuntimeEvent
from .modes import RuntimeMode


class RuntimeState(BaseModel):
    """
    Represents the current state of the Terminal Agent runtime.

    The Runtime Kernel is the sole owner of this model.
    """

    mode: RuntimeMode = RuntimeMode.INITIALIZING

    last_event: RuntimeEvent | None = None

    iteration: int = 0

    started_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
    
class RuntimeSnapshot(BaseModel):
    """
    Read-only snapshot of the runtime state.
    """

    mode: RuntimeMode

    last_event: RuntimeEvent | None

    iteration: int
    
def snapshot_runtime(
    runtime_state: RuntimeState,
) -> RuntimeSnapshot:
    return RuntimeSnapshot(
        mode=runtime_state.mode,
        last_event=runtime_state.last_event,
        iteration=runtime_state.iteration,
    )