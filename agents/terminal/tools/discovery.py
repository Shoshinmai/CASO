import string
from pathlib import Path

from langchain_core.tools import tool

from agents.terminal.models import ListDirectoryInput
from agents.terminal.utils.location_resolver import resolve_location
from agents.terminal.utils.filesystem_helpers import safe_walk

# from .terminal.utils.location_resolver import resolve_location


MAX_RESULTS = 100
MAX_DIRECTORY_RESULTS = 500


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
    # search_files.category = "Discovery"

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


@tool(args_schema=ListDirectoryInput)
def list_directory(
    location: str = "current directory",
    recursive: bool = False,
    include_hidden: bool = False,
    max_depth: int = 2,
) -> dict:
    """
    PURPOSE
    -------
    Inspect the structure and contents of a directory.

    This capability helps the planner understand how files
    and folders are organized before selecting files to read
    or modify.

    TYPICAL USE CASES
    -----------------
    - Explore a project.
    - Inspect an unfamiliar folder.
    - Locate configuration directories.
    - Understand repository layout.
    - Count files and folders.

    USE THIS CAPABILITY WHEN
    ------------------------
    - The directory structure is unknown.
    - The planner needs to discover where files are located.
    - Browsing folders is more appropriate than searching by filename.

    DO NOT USE THIS CAPABILITY WHEN
    -------------------------------
    - Searching for a known filename.
      Use search_files.

    - Reading file contents.
      Use read_file.

    - Searching inside files.
      Use search_content.

    - Executing shell commands.
      Use run_terminal only if no specialized capability applies.

    IMPORTANT
    ---------
    Directory exploration should normally precede reading
    or modifying files in unfamiliar locations.
    Maximum traversal depth is controlled by the max_depth argument.

    Returns
    -------
    Structured directory information including folders,
    files, summary counts, and traversal metadata.
    """

#     list_directory.category = "Discovery"
#     list_directory.return_description = """
# Returns:

# - success
# - resolved_path
# - directories
# - files
# - total_directories
# - total_files
# - recursive
# - truncated
# """
#     list_directory.usage_notes = """
# Use this capability to inspect a directory.

# Do not use it to locate files by name.

# Use search_files instead.

# Do not use it to read files.

# Use read_file instead.
# """
    try:
        root_path = resolve_location(location)

    except ValueError as e:

        return {
            "success": False,
            "location": location,
            "error": str(e),
        }

    directories = []
    files = []

    total_directories = 0
    total_files = 0

    for entry in safe_walk(
        root=root_path,
        recursive=recursive,
        include_hidden=include_hidden,
        max_depth=max_depth,
    ):
        relative = entry.relative_to(root_path)

        if entry.is_dir():

            directories.append(str(relative))
            total_directories += 1

        else:

            files.append(str(relative))
            total_files += 1

    truncated = False

    if len(directories) > MAX_DIRECTORY_RESULTS:

        directories = directories[:MAX_DIRECTORY_RESULTS]
        truncated = True

    remaining = MAX_DIRECTORY_RESULTS - len(directories)

    if remaining < 0:
        remaining = 0

    if len(files) > remaining:

        files = files[:remaining]
        truncated = True

    return {
        "success": True,
        "location": location,
        "resolved_path": str(root_path),
        "directories": directories,
        "files": files,
        "total_directories": total_directories,
        "total_files": total_files,
        "recursive": recursive,
        "truncated": truncated,
    }


# print(search_files.invoke({"query": "main.py"}))
