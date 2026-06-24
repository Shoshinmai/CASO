from typing import TypedDict
class TerminalState(TypedDict):

    goal: str

    action_type: str
    thought: str
    command: str

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
    artifact_ids: list[str]