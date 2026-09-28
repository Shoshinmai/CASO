import pytest

from agents.terminal.evidence.models import (
    EvidenceRecord,
    EvidenceProvenance,
)
from agents.terminal.evidence.store import (
    InMemoryEvidenceStore,
)


def make_evidence(
    *,
    evidence_id: str,
    tool_name: str = "run_terminal",
    resource_ref: str = "repo/file.py",
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        content=f"Evidence content for {evidence_id}",
        provenance=EvidenceProvenance(
            tool_name=tool_name,
            attempt=1,
        ),
        resource_refs=[resource_ref],
        structured_data={
            "execution": {
                "stdout": f"output-{evidence_id}",
            },
        },
    )


@pytest.mark.asyncio
async def test_evidence_is_stored_by_thread():
    store = InMemoryEvidenceStore()

    evidence = make_evidence(
        evidence_id="evidence-1",
    )

    await store.add(
        "thread-a",
        evidence,
    )

    result = await store.get(
        "thread-a",
        "evidence-1",
    )

    assert result is evidence


@pytest.mark.asyncio
async def test_evidence_is_isolated_between_threads():
    store = InMemoryEvidenceStore()

    evidence_a = make_evidence(
        evidence_id="evidence-a",
    )

    evidence_b = make_evidence(
        evidence_id="evidence-b",
    )

    await store.add(
        "thread-a",
        evidence_a,
    )

    await store.add(
        "thread-b",
        evidence_b,
    )

    assert (
        await store.get(
            "thread-a",
            "evidence-a",
        )
    ) is evidence_a

    assert (
        await store.get(
            "thread-b",
            "evidence-b",
        )
    ) is evidence_b

    assert (
        await store.get(
            "thread-a",
            "evidence-b",
        )
    ) is None

    assert (
        await store.get(
            "thread-b",
            "evidence-a",
        )
    ) is None


@pytest.mark.asyncio
async def test_multiple_executions_are_retained_in_same_thread():
    store = InMemoryEvidenceStore()

    evidence_1 = make_evidence(
        evidence_id="evidence-1",
    )

    evidence_2 = make_evidence(
        evidence_id="evidence-2",
    )

    await store.add(
        "thread-a",
        evidence_1,
    )

    await store.add(
        "thread-a",
        evidence_2,
    )

    results = await store.list(
        "thread-a",
    )

    assert len(results) == 2

    assert {
        evidence.evidence_id
        for evidence in results
    } == {
        "evidence-1",
        "evidence-2",
    }


@pytest.mark.asyncio
async def test_list_filters_without_crossing_thread_boundary():
    store = InMemoryEvidenceStore()

    terminal_evidence = make_evidence(
        evidence_id="terminal",
        tool_name="run_terminal",
        resource_ref="repo/a.py",
    )

    file_evidence = make_evidence(
        evidence_id="file",
        tool_name="read_file",
        resource_ref="repo/b.py",
    )

    other_thread_evidence = make_evidence(
        evidence_id="other-thread",
        tool_name="run_terminal",
        resource_ref="repo/a.py",
    )

    await store.add(
        "thread-a",
        terminal_evidence,
    )

    await store.add(
        "thread-a",
        file_evidence,
    )

    await store.add(
        "thread-b",
        other_thread_evidence,
    )

    terminal_results = await store.list(
        "thread-a",
        tool_name="run_terminal",
    )

    assert [
        evidence.evidence_id
        for evidence in terminal_results
    ] == ["terminal"]

    resource_results = await store.list(
        "thread-a",
        resource_ref="repo/a.py",
    )

    assert [
        evidence.evidence_id
        for evidence in resource_results
    ] == ["terminal"]

    # Evidence belonging to another thread must never appear.
    all_thread_a = await store.list(
        "thread-a",
    )

    assert {
        evidence.evidence_id
        for evidence in all_thread_a
    } == {
        "terminal",
        "file",
    }