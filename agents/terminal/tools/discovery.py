import string
from pathlib import Path

from langchain_core.tools import tool

from agents.terminal.utils.location_resolver import resolve_location

# from .terminal.utils.location_resolver import resolve_location


MAX_RESULTS = 100


@tool
def search_files(
    query: str,
    location: str = "current directory",
    recursive: bool = True,
    case_sensitive: bool = False,
) -> dict:
    """
    PURPOSE
    -------
    Locate files when their exact location is unknown.

    This capability searches for files by filename or filename pattern
    within a specified location.

    Use this capability before attempting to read or modify a file whose
    location is not yet known.

    TYPICAL USE CASES
    -----------------
    - Find a file by name.
    - Locate source code files.
    - Search for configuration files.
    - Locate logs or reports.

    USE THIS CAPABILITY WHEN
    ------------------------
    - The user knows the filename but not its location.
    - A file must be located before reading or editing.
    - Searching by filename is sufficient.

    DO NOT USE THIS CAPABILITY WHEN
    -------------------------------
    - Exploring an unknown directory structure.
      Use list_directory.

    - Searching inside file contents.
      Use search_content.

    - Reading a file.
      Use read_file.

    - Executing shell commands.
      Use run_terminal only if no specialized capability applies.

    IMPORTANT
    ---------
    Repeating this capability with only minor changes to the search
    query is usually not a new strategy.

    If previous searches have clearly failed, consider another
    capability instead.

    Returns
    -------
    Structured search results containing matched files and metadata.
    """

    try:
        root_path = resolve_location(location)
    except ValueError as e:
        return {
            "success": False,
            "query": query,
            "location": location,
            "count": 0,
            "matches": [],
            "truncated": False,
            "error": str(e),
        }
    max_results = MAX_RESULTS

    matches = []

    try:
        iterator = root_path.rglob("*") if recursive else root_path.glob("*")

        for path in iterator:

            if not path.is_file():
                continue

            filename = path.name if case_sensitive else path.name.lower()
            search_query = query if case_sensitive else query.lower()

            if search_query in filename:
                matches.append(str(path.resolve()))

                if len(matches) >= max_results:
                    break

        return {
            "success": True,
            "query": query,
            "root": str(root_path.resolve()),
            "count": len(matches),
            "matches": matches,
            "truncated": len(matches) >= max_results,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "query": query,
        }


print(search_files.invoke({"query": "main.py"}))
