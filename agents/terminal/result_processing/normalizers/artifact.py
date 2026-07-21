from agents.terminal.result_processing.models import (
    ArtifactCandidate,
    ExecutionOutcome,
    Fact,
    NormalizedResult,
    Resource,
    ToolExecutionContext,
)


def _build_normalized_result(
    *,
    tool_name: str,
    attempt: int,
    success: bool,
    progress_made: bool,
    facts: list[Fact],
    resources: list[Resource],
    artifact: ArtifactCandidate | None,
) -> NormalizedResult:
    """
    Construct a NormalizedResult shared by filesystem
    discovery normalizers.
    """

    return NormalizedResult(
        context=ToolExecutionContext(
            tool_name=tool_name,
            attempt=attempt,
        ),
        execution=ExecutionOutcome(
            success=success,
            progress_made=progress_made,
            message=None,
        ),
        facts=facts,
        resources=resources,
        artifact=artifact,
    )


def normalize_search_artifact(
    *,
    tool_name: str,
    raw_result: dict,
    attempt: int = 1,
) -> NormalizedResult:
    """
    Normalize search_artifact results.
    """

    if not raw_result.get("success", False):
        return _build_normalized_result(
            tool_name=tool_name,
            attempt=attempt,
            success=False,
            progress_made=False,
            facts=[],
            resources=[],
            artifact=None,
        )

    query = raw_result["query"]
    count = raw_result["count"]
    artifact_id = raw_result["artifact_id"]

    facts = [
        Fact(
            statement=(
                f'Found {count} matches for "{query}" ' f'in artifact "{artifact_id}".'
            ),
            source=tool_name,
        ),
    ]

    if raw_result.get("truncated", False):
        facts.append(
            Fact(
                statement="Artifact search results were truncated.",
                source=tool_name,
            )
        )

    return _build_normalized_result(
        tool_name=tool_name,
        attempt=attempt,
        success=True,
        progress_made=bool(count),
        facts=facts,
        resources=[],
        artifact=None,
    )


def normalize_read_artifact(
    *,
    tool_name: str,
    raw_result: dict,
    attempt: int = 1,
) -> NormalizedResult:
    """
    Normalize read_artifact results.
    """

    if not raw_result.get("success", False):
        return _build_normalized_result(
            tool_name=tool_name,
            attempt=attempt,
            success=False,
            progress_made=False,
            facts=[],
            resources=[],
            artifact=None,
        )

    artifact_id = raw_result["artifact_id"]

    start_line = raw_result["start_line"]
    end_line = raw_result["end_line"]

    facts = [
        Fact(
            statement=(
                f"Read artifact {artifact_id} " f"(lines {start_line}-{end_line})."
            ),
            source=tool_name,
        ),
    ]

    if raw_result.get("has_more", False):
        facts.append(
            Fact(
                statement="Additional artifact content is available.",
                source=tool_name,
            )
        )

    return _build_normalized_result(
        tool_name=tool_name,
        attempt=attempt,
        success=True,
        progress_made=True,
        facts=facts,
        resources=[],
        artifact=None,
    )
