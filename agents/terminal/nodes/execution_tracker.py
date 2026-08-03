from agents.terminal.memory.execution_manager import ExecutionMemoryManager
from agents.terminal.models import EphemeralExecutionState
from agents.terminal.state import TerminalState


def execution_tracker_node(state: TerminalState) -> dict:
    """
    Initialize execution tracking for the next tool invocation.

    This node creates an ExecutionAttempt before the ToolNode executes.
    It performs runtime bookkeeping only and does not execute tools or
    determine execution success.
    """

    planner_output = state.get("planner_output")

    if planner_output is None:
        return {}

    planning_step = planner_output.planning_step

    if planning_step is None:
        return {}

    ephemeral = state.get("ephemeral_execution_state")

    if ephemeral is None:
        ephemeral = EphemeralExecutionState()

    attempt = ExecutionMemoryManager.start_attempt(
        execution_memory=state["execution_memory"],
        capability=planning_step.capability,
        strategy=planning_step.strategy,
        arguments=planning_step.args,
    )

    ephemeral.current_attempt_id = attempt.attempt_id

    if (
        ephemeral.current_attempt_id is not None
        and ExecutionMemoryManager.current_attempt(state["execution_memory"])
        is not None
    ):
        return {
            "execution_memory": state["execution_memory"],
            "ephemeral_execution_state": ephemeral,
        }