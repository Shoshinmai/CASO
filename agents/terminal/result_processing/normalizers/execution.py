from agents.terminal.result_processing.models import (
    ArtifactCandidate,
    ExecutionOutcome,
    Fact,
    NormalizedResult,
    ToolExecutionContext,
)


def _build_normalized_result(
    *,
    tool_name: str,
    attempt: int,
    success: bool,
    progress_made: bool,
    facts: list[Fact],
    artifact: ArtifactCandidate | None,
) -> NormalizedResult:
    """
    Construct a NormalizedResult for execution capabilities.
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
        resources=[],
        artifact=artifact,
    )


def normalize_run_terminal(
    *,
    tool_name: str,
    raw_result: dict,
    attempt: int = 1,
) -> NormalizedResult:
    """
    Normalize run_terminal results.
    """

    success = raw_result.get("success", False)

    facts = [
        Fact(
            statement=(
                "Terminal command executed successfully."
                if success
                else "Terminal command execution failed."
            ),
            source=tool_name,
        ),
        Fact(
            statement=(
                f"Exit code: {raw_result.get('return_code', -1)}."
            ),
            source=tool_name,
        ),
    ]

    output = raw_result.get("output", "")
    error = raw_result.get("error", "")

    artifact = ArtifactCandidate(
        artifact_type="terminal_output",
        summary=(
            "Terminal command output."
            if success
            else "Terminal command failed."
        ),
        data={
            "output": output,
            "error": error,
            "return_code": raw_result.get("return_code"),
        },
    )

    return _build_normalized_result(
        tool_name=tool_name,
        attempt=attempt,
        success=success,
        progress_made=success,
        facts=facts,
        artifact=artifact,
    )