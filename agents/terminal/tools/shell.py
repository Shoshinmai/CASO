from langchain_core.tools import tool

from agents.terminal.tools.command_runner import run_command


@tool
def run_terminal(command: str) -> dict:
    """
    PURPOSE
    -------
    Execute a single Windows terminal command.

    This is the fallback capability of the Terminal Agent.

    Prefer specialized capabilities whenever they can accomplish
    the user's goal.

    USE THIS CAPABILITY WHEN
    ------------------------
    - No specialized capability exists.
    - Git operations.
    - Python execution.
    - Package managers.
    - Windows utilities.
    - System inspection.
    - Environment diagnostics.
    - Network utilities.
    - Custom shell workflows.

    DO NOT USE THIS CAPABILITY WHEN
    -------------------------------
    - search_files can locate the file.
    - list_directory can inspect folders.
    - read_file can read the required file.
    - replace_text can modify a file.
    - Any other specialized capability directly solves the task.

    COMMAND RULES
    -------------
    - Generate exactly ONE command.
    - Never chain commands.
    - Do not use && or ||.
    - Prefer read-only commands unless the user's request explicitly
      requires modification.

    IMPORTANT
    ---------
    This capability should only be selected after specialized
    capabilities have been considered.

    Returns
    -------
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
