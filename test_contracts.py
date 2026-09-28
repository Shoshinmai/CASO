import pytest

from agents.terminal.evidence.models import (
    EvidenceProvenance,
    EvidenceRecord,
    EvidenceRetrievalQuery,
)
from agents.terminal.retrieval.models import (
    EvidenceRetrievalResult,
    RetrievedEvidence,
    SearchDocument,
)


def make_evidence() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="evidence-1",
        content="Task execution is coordinated by the runtime.",
        provenance=EvidenceProvenance(
            tool_name="run_terminal",
            attempt=1,
        ),
        resource_refs=[
            "agents/terminal/runtime",
        ],
        structured_data={
            "execution": {
                "stdout": "example",
            },
        },
    )


def test_search_document_represents_evidence():
    document = SearchDocument(
        document_id="doc-1",
        evidence_id="evidence-1",
        text="Task execution is coordinated by the runtime.",
        thread_id="thread-a",
        resource_refs=[
            "agents/terminal/runtime",
        ],
        tool_name="run_terminal",
    )

    assert document.evidence_id == "evidence-1"
    assert document.thread_id == "thread-a"
    assert document.text


def test_retrieved_evidence_contains_ranking_metadata():
    evidence = make_evidence()

    retrieved = RetrievedEvidence(
        evidence=evidence,
        score=0.91,
        rank=1,
        source="semantic",
    )

    assert retrieved.evidence is evidence
    assert retrieved.score == 0.91
    assert retrieved.rank == 1
    assert retrieved.source == "semantic"


def test_retrieval_result_wraps_ranked_evidence():
    evidence = make_evidence()

    query = EvidenceRetrievalQuery(
        query="How is task execution coordinated?",
        limit=5,
    )

    retrieved = RetrievedEvidence(
        evidence=evidence,
        score=0.91,
        rank=1,
        source="semantic",
    )

    result = EvidenceRetrievalResult(
        query=query,
        results=[retrieved],
        total_candidates=1,
    )

    assert result.query == query
    assert len(result.results) == 1
    assert result.results[0].rank == 1
    assert result.total_candidates == 1


def test_invalid_retrieved_rank_is_rejected():
    evidence = make_evidence()

    with pytest.raises(ValueError):
        RetrievedEvidence(
            evidence=evidence,
            score=0.5,
            rank=0,
            source="semantic",
        )


def test_retrieval_query_rejects_empty_query():
    with pytest.raises(ValueError):
        EvidenceRetrievalQuery(
            query="",
        )