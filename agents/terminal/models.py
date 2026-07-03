from typing import Any, Literal
from pydantic import BaseModel, Field


class TerminalAction(BaseModel):

    action_type: Literal["terminal_command", "artifact_query", "tool_call"]

    thought: str

    command: str = ""

    tool_name: str = ""

    tool_input: str = ""


class EvaluatorDecision(BaseModel):
    decision: Literal["DONE", "CONTINUE"]


class ObservationSummary(BaseModel):
    summary: str


class ObservationDecision(BaseModel):

    memory_strategy: Literal[
        "pass_through", "store_artifact", "store_and_summarize", "discard"
    ]

    artifact_type: Literal[
        "file_listing",
        "package_list",
        "log",
        "git_diff",
        "command_output",
        "system_command",
    ]

    summary: str

    important_information: str

    reasoning: str 

    conclusion: str
    # summary: str = Field(min_length=1)

    # important_information: str = ""

    # reasoning: str = Field(min_length=1)

    # conclusion: str = Field(min_length=1)

class ObservationInput(BaseModel):

    source: str

    tool_name: str | None = None

    success: bool

    raw_result: dict | str

class PlanningStep(BaseModel):
    """
    Single planning decision produced by the planner.
    """

    strategy: str = Field(
        description="High-level strategy for the next step."
    )

    capability: str = Field(
        description="Capability selected for execution."
    )

    args: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the selected capability."
    )


class PlanningOutput(BaseModel):
    """
    Complete planner response.

    Additional planning metadata can be added later without
    changing the graph contract.
    """

    planning_step: PlanningStep