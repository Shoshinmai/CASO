from typing import Literal
from pydantic import BaseModel


class TerminalAction(BaseModel):
    thought: str
    command: str


class EvaluatorDecision(BaseModel):
    decision: Literal["DONE", "CONTINUE"]
    
class ObservationSummary(BaseModel):
    summary: str