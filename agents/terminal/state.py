from typing import Literal, Optional, TypedDict
from typing import Annotated

from langgraph.graph.message import add_messages

from langchain_core.messages import AnyMessage

from agents.terminal.models import ObservationInput, PlanningOutput


class TerminalState(TypedDict):

    goal: str
    messages: Annotated[list[AnyMessage], add_messages]
    action_type: str
    thought: str
    command: str
    tool_name: str
    tool_input: str

    success: bool
    error: str

    done: bool
    step_count: int

    scratchpad: str

    valid_command: bool
    validation_error: str

    safety_passed: bool
    safety_reason: str

    raw_observation: str
    compressed_observation: str
    observation_input: ObservationInput | None
    artifact_ids: list[str]
    artifact_type: Literal[
        "file_listing", "package_list", "log", "git_diff", "command_output"
    ]

    observation_summary: str

    observation_conclusion: str

    planner_output: Optional[PlanningOutput] = None