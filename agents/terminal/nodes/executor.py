from agents.terminal.state import TerminalState
from agents.terminal.tools.command_runner import run_command


def terminal_executor_node(state: TerminalState):

    result = run_command(state["command"])

    observation = result["stdout"] if result["stdout"] else result["stderr"]

    return {
        "raw_observation": observation,
        "error": result["stderr"],
        "success": result["returncode"] == 0,
    }
