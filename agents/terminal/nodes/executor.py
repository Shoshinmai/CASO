from agents.terminal.tools.command_runner import (
    run_command
)


def terminal_executor_node(state):

    result = run_command(
        state["command"]
    )

    return {
        "output": result["stdout"],
        "error": result["stderr"],
        "success": result["returncode"] == 0
    }