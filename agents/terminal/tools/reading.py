from langchain_core.tools import tool

from agents.terminal.models import ReadFileInput
from agents.terminal.utils.location_resolver import resolve_location
from agents.terminal.utils.text_helpers import read_lines


@tool(args_schema=ReadFileInput)
def read_file(
    path: str,
    start_line: int = 1,
    max_lines: int = 200,
) -> dict:
    """
    PURPOSE
    -------
    Read a bounded window of lines from a text file.

    This capability allows the Terminal Agent to inspect file contents
    without loading the entire file into the model context.

    TYPICAL USE CASES
    -----------------
    - Inspect source code.
    - Read configuration files.
    - Examine logs around a relevant location.
    - Continue reading a large file using pagination.
    - Inspect a file found by search_files.
    - Read context around a match found by search_content.

    USE THIS CAPABILITY WHEN
    ------------------------
    - The file path is known.
    - File contents need to be inspected.
    - A bounded section of a large file needs to be read.

    DO NOT USE THIS CAPABILITY WHEN
    -------------------------------
    - Searching for a file by name.
      Use search_files.

    - Searching for text across files.
      Use search_content.

    - Exploring a directory structure.
      Use list_directory.

    - Executing commands.
      Use run_terminal only when no specialized capability applies.

    IMPORTANT
    ---------
    This capability performs bounded, windowed reading.

    Use start_line to begin reading from a specific line.

    Use max_lines to control the maximum number of lines returned.

    If has_more is true, use next_start_line to continue reading the file.

    Returns
    -------
    Structured file content with pagination metadata.
    """

    try:
        resolved_path = resolve_location(path)

    except ValueError as exc:
        return {
            "success": False,
            "path": path,
            "error": str(exc),
        }

    if not resolved_path.is_file():
        return {
            "success": False,
            "path": str(resolved_path),
            "error": "Path is not a file.",
        }

    result = read_lines(
        path=resolved_path,
        start_line=start_line,
        max_lines=max_lines,
    )

    if result is None:
        return {
            "success": False,
            "path": str(resolved_path),
            "error": "Unable to read file.",
        }

    return {
        "success": True,
        "path": str(resolved_path),
        **result,
    }