from langchain_core.tools import tool

from agents.terminal.tools.command_runner import run_command


@tool
def run_terminal(command: str) -> dict:
    """
    Execute a single Windows terminal command.

    PURPOSE
    -------
    This is the fallback capability of the Terminal Agent.

    Use this tool ONLY when no specialized capability can
    accomplish the requested task.

    Prefer specialized tools whenever they are capable of
    solving the user's request.

    Typical use cases:

    - commands not covered by existing tools
    - filesystem operations unavailable through specialized tools
    - git commands
    - python execution
    - package managers
    - system inspection
    - network utilities
    - Windows administration
    - command-line utilities

    Do NOT use this tool when another capability already
    provides the same functionality.

    The command must be exactly ONE terminal command.

    Do not chain commands.

    Args:
        command:
            A complete executable Windows command.

    Returns:
        stdout
        stderr
        return_code
        success
    """

    result = run_command(command)

    return {
        "success": result["returncode"] == 0,
        "output": result["stdout"],
        "error": result["stderr"],
        "return_code": result["returncode"],
    }


# print(run_terminal.invoke({"command": "where python"}))
