import pytest

from agents.terminal.models import ActiveTaskMemory
from agents.terminal.result_processing.models import (
    MemoryUpdateProposal,
)
from agents.terminal.result_processing.processor import (
    process_tool_result,
)
from agents.terminal.state import TerminalState


def make_state() -> TerminalState:
    return {
        "goal": "Inspect the terminal runtime.",
        "active_memory": ActiveTaskMemory(
            known_facts=[],
            discovered_resources=[],
            completed_work=[],
            unresolved_needs=[],
        ),
    }


@pytest.mark.asyncio
async def test_process_tool_result_emits_evidence(
    monkeypatch,
):
    async def fake_condense_memory(
        *,
        goal,
        active_memory,
        formatted_observation,
        tool_name,
    ):
        return MemoryUpdateProposal()

    monkeypatch.setattr(
        "agents.terminal.result_processing.processor.condense_memory",
        fake_condense_memory,
    )

    raw_result = {
    "success": True,
    "return_code": 0,
    "output": "hello terminal",
    "error": "",
}

    result = await process_tool_result(
        state=make_state(),
        tool_name="run_terminal",
        raw_result=raw_result,
        attempt=1,
    )

    # Existing processing result remains intact.
    assert result.normalized_result is not None
    assert result.artifact_decision is not None
    assert result.memory_update is not None

    # Prototype 3 evidence is produced.
    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.provenance.tool_name == "run_terminal"
    assert evidence.provenance.attempt == 1
    
    assert evidence.structured_data["execution"]["success"] is True
    assert evidence.structured_data["execution"]["return_code"] == 0

    assert evidence.structured_data["execution"]["stdout"] == "hello terminal"


@pytest.mark.asyncio
async def test_process_tool_result_evidence_matches_normalized_result(
    monkeypatch,
):
    async def fake_condense_memory(
        *,
        goal,
        active_memory,
        formatted_observation,
        tool_name,
    ):
        return MemoryUpdateProposal()

    monkeypatch.setattr(
        "agents.terminal.result_processing.processor.condense_memory",
        fake_condense_memory,
    )

    raw_result = {
    "success": True,
    "return_code": 0,
    "output": "python output",
    "error": "",
}

    result = await process_tool_result(
        state=make_state(),
        tool_name="run_terminal",
        raw_result=raw_result,
        attempt=3,
    )

    evidence = result.evidence[0]
    normalized = result.normalized_result

    # Evidence must describe the same execution.
    assert evidence.provenance.tool_name == normalized.context.tool_name

    assert evidence.provenance.attempt == normalized.context.attempt

    assert (
        evidence.structured_data["execution"]["success"] == normalized.execution.success
    )

    assert (
        evidence.structured_data["execution"]["stdout"] == normalized.execution.stdout
    )


@pytest.mark.asyncio
async def test_evidence_generation_does_not_mutate_active_memory(
    monkeypatch,
):
    async def fake_condense_memory(
        *,
        goal,
        active_memory,
        formatted_observation,
        tool_name,
    ):
        return MemoryUpdateProposal()

    monkeypatch.setattr(
        "agents.terminal.result_processing.processor.condense_memory",
        fake_condense_memory,
    )

    state = make_state()

    original_memory = state["active_memory"].model_copy(deep=True)
    assert state["active_memory"] == original_memory

    raw_result = {
    "success": True,
    "return_code": 0,
    "output": "test output",
    "error": "",
}

    result = await process_tool_result(
        state=state,
        tool_name="run_terminal",
        raw_result=raw_result,
    )

    assert len(result.evidence) == 1

    # process_tool_result() must remain non-mutating.
    assert state["active_memory"] == original_memory
