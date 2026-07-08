from pathlib import Path
from typing import Optional
import shutil

DEFAULT_ENCODING = "utf-8"

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

MAX_READ_LINES = 1000


def is_binary_file(path: Path) -> bool:
    """
    Return True if the file appears to be binary.

    Reads only a small sample of the file.
    """

    try:
        with path.open("rb") as f:
            chunk = f.read(1024)

        return b"\x00" in chunk

    except Exception:
        return True


def safe_read_text(
    path: Path,
    encoding: str = DEFAULT_ENCODING,
    max_lines: int = MAX_READ_LINES,
) -> Optional[str]:

    if not path.exists():
        return None

    if not path.is_file():
        return None

    if path.stat().st_size > MAX_FILE_SIZE:
        return None

    if is_binary_file(path):
        return None

    try:

        with path.open(
            "r",
            encoding=encoding,
            errors="replace",
        ) as f:

            lines = []

            for i, line in enumerate(f):

                if i >= max_lines:
                    break

                lines.append(line)

            return "".join(lines)

    except Exception:

        return None


def read_lines(
    path: Path,
    start_line: int = 1,
    max_lines: int = 200,
    encoding: str = DEFAULT_ENCODING,
) -> Optional[dict]:
    """
    Read a bounded window of lines from a text file.

    Lines are 1-indexed.

    Reads one additional line beyond the requested window to
    determine whether more content exists.

    Returns structured pagination metadata and file content,
    or None if the file cannot be read.
    """

    if start_line < 1:
        return None

    if max_lines < 1:
        return None

    if not path.exists():
        return None

    if not path.is_file():
        return None

    if is_binary_file(path):
        return None

    requested_end_line = start_line + max_lines - 1

    try:
        collected_lines = []
        has_more = False

        with path.open(
            "r",
            encoding=encoding,
            errors="replace",
        ) as file:

            for line_number, line in enumerate(file, start=1):

                if line_number < start_line:
                    continue

                if line_number <= requested_end_line:
                    collected_lines.append(line)
                    continue

                has_more = True
                break

        lines_returned = len(collected_lines)

        actual_end_line = (
            start_line + lines_returned - 1
            if lines_returned > 0
            else None
        )

        next_start_line = (
            actual_end_line + 1
            if has_more and actual_end_line is not None
            else None
        )

        return {
            "start_line": start_line,
            "end_line": actual_end_line,
            "lines_returned": lines_returned,
            "has_more": has_more,
            "next_start_line": next_start_line,
            "content": "".join(collected_lines),
        }

    except (PermissionError, OSError, UnicodeError):
        return None

def find_search_backend() -> str:
    """
    Detect the best available text search backend.

    Priority:
        1. ripgrep
        2. grep
        3. python
    """

    if shutil.which("rg"):
        return "ripgrep"

    # if shutil.which("grep"):
    #     return "grep"

    return "python"