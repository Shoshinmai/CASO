import string
from pathlib import Path

from langchain_core.tools import tool


MAX_RESULTS = 100


@tool
def search_files(
    query: str,
    location: str = "workspace",
) -> dict:
    """
    Search recursively for files or folders whose names match a query.

    Use this tool whenever you need to locate a file or folder before performing
    another action such as reading, opening, moving, or editing it.

    Args:
        query:
            Full or partial name of the file or folder.

        location:
            Natural language search location.

            Examples:
                - workspace
                - project
                - current directory
                - desktop
                - downloads
                - documents
                - pictures
                - music
                - videos
                - C drive
                - D drive
                - E drive
                - all drives

    Returns:
        A dictionary containing:

        - success: Whether the search completed successfully.
        - query: The original search query.
        - root: The resolved search location.
        - count: Number of matches found.
        - matches: Matching file or folder paths.
        - truncated: Whether the result list was truncated.
    """

    root_path = resolve_location(location)
    max_results = MAX_RESULTS

    matches = []

    try:
        for path in root_path.rglob("*"):

            if not path.is_file():
                continue

            if query.lower() in path.name.lower():
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


def resolve_location(location: str):

    locations = get_search_locations()

    normalized = location.lower().strip()

    ALIASES = {
        "my desktop": "desktop",
        "desktop folder": "desktop",
        "my downloads": "downloads",
        "download folder": "downloads",
        "current project": "project",
        "project root": "project",
        "working directory": "current directory",
    }
    normalized = ALIASES.get(normalized, normalized)

    if normalized in locations:
        return locations[normalized]

    return Path.cwd()


def get_available_drives() -> dict[str, Path]:

    drives = {}

    for letter in string.ascii_uppercase:

        drive = Path(f"{letter}:\\")

        if drive.exists():
            drives[f"{letter.lower()} drive"] = drive
            drives[f"{letter}:"] = drive
            drives[letter.lower()] = drive

    return drives


def get_user_locations() -> dict[str, Path]:

    home = Path.home()

    folders = {}

    candidates = {
        "desktop": home / "Desktop",
        "documents": home / "Documents",
        "downloads": home / "Downloads",
        "pictures": home / "Pictures",
        "videos": home / "Videos",
        "music": home / "Music",
    }

    for name, path in candidates.items():
        if path.exists():
            folders[name] = path

    return folders


def get_search_locations():

    locations = {
        "workspace": Path.cwd(),
        "project": Path.cwd(),
        "current directory": Path.cwd(),
        "current folder": Path.cwd(),
    }

    locations.update(get_user_locations())
    locations.update(get_available_drives())

    return locations


# print(search_files.invoke({"query": "e"}))
