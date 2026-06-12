from typing import TypedDict


class TerminalState(TypedDict):

    goal: str

    command: str

    output: str

    error: str

    success: bool

    retry_count: int

    safe: bool

    critic_decision: str

    critic_feedback: str