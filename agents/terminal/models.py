from typing import Literal
from pydantic import BaseModel


class TerminalAction(BaseModel):

    action_type: Literal["terminal_command", "artifact_query"]
    thought: str
    command: str


class EvaluatorDecision(BaseModel):
    decision: Literal["DONE", "CONTINUE"]


class ObservationSummary(BaseModel):
    summary: str


class ObservationDecision(BaseModel):

    category: Literal["small_output", "file_listing", "large_text", "disposable"]

    needs_artifact: bool

    summary: str
