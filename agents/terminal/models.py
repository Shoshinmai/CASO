from typing import Any, Literal
from pydantic import BaseModel, Field


class TerminalAction(BaseModel):

    action_type: Literal["terminal_command", "artifact_query", "tool_call"]

    thought: str

    command: str = ""

    tool_name: str = ""

    tool_input: str = ""


class EvaluatorDecision(BaseModel):
    decision: Literal["DONE", "CONTINUE"]


class ObservationSummary(BaseModel):
    summary: str


class ObservationDecision(BaseModel):

    memory_strategy: Literal[
        "pass_through", "store_artifact", "store_and_summarize", "discard"
    ]

    artifact_type: Literal[
        "file_listing",
        "package_list",
        "log",
        "git_diff",
        "command_output",
        "system_command",
    ]

    summary: str

    important_information: str

    reasoning: str 

    conclusion: str
    # summary: str = Field(min_length=1)

    # important_information: str = ""

    # reasoning: str = Field(min_length=1)

    # conclusion: str = Field(min_length=1)

class ObservationInput(BaseModel):

    source: str

    tool_name: str | None = None

    success: bool

    raw_result: dict | str

class PlanningStep(BaseModel):
    """
    Single planning decision produced by the planner.
    """

    strategy: str = Field(
        description="High-level strategy for the next step."
    )

    capability: str = Field(
        description="Capability selected for execution."
    )

    args: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the selected capability."
    )


class PlanningOutput(BaseModel):
    """
    Complete planner response.

    Additional planning metadata can be added later without
    changing the graph contract.
    """

    planning_step: PlanningStep
    
class ListDirectoryInput(BaseModel):
    """
    Input schema for listing the contents of a directory.
    """

    location: str = Field(
        default="current directory",
        description=(
            "Directory to inspect. Supports natural language locations "
            "such as current directory, project, desktop, downloads, "
            "documents, pictures, videos, music, C drive, D drive, etc."
        ),
    )

    recursive: bool = Field(
        default=False,
        description="Whether to recursively traverse subdirectories."
    )

    include_hidden: bool = Field(
        default=False,
        description="Include hidden files and folders."
    )

    max_depth: int = Field(
        default=2,
        ge=1,
        le=20,
        description="Maximum recursion depth when recursive=True."
    )
    
class SearchContentInput(BaseModel):
    """
    Input schema for searching text inside files.
    """

    query: str = Field(
        description="Text or pattern to search for."
    )

    location: str = Field(
        default="current directory",
        description=(
            "Natural language search location."
        ),
    )

    file_pattern: str = Field(
        default="*",
        description=(
            "Glob pattern limiting which files are searched."
        ),
    )

    case_sensitive: bool = Field(
        default=False,
        description="Perform case-sensitive matching."
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of matching files."
    )

class ReadFileInput(BaseModel):
    """
    Input schema for reading a bounded window of a text file.
    """

    path: str = Field(
        description=(
            "Path of the text file to read. Supports absolute "
            "and relative filesystem paths."
        )
    )

    start_line: int = Field(
        default=1,
        ge=1,
        description=(
            "First line to read. Lines are 1-indexed."
        ),
    )

    max_lines: int = Field(
        default=200,
        ge=1,
        le=1000,
        description=(
            "Maximum number of lines to return."
        ),
    )