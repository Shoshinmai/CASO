import json

from agents.terminal.evidence.models import (
    EvidenceProvenance,
    EvidenceRecord,
    EvidenceSourceType,
)
from agents.terminal.retrieval.search_document import (
    DeterministicSearchDocumentBuilder,
)


def make_evidence(
    *,
    evidence_id: str = "evidence-1",
) -> EvidenceRecord:
    structured_data = {
        "facts": [
            {
                "statement": (
                    "The runtime uses concurrent execution."
                ),
                "source": "run_terminal",
            }
        ],
        "resources": [
            {
                "type": "file",
                "identifier": (
                    "agents/terminal/runtime_graph.py"
                ),
                "metadata": {},
            }
        ],
        "execution": {
            "success": True,
            "progress_made": True,
            "message": "Completed.",
            "return_code": 0,
            "stdout": "runtime output",
            "stderr": "",
        },
    }

    return EvidenceRecord(
        evidence_id=evidence_id,
        content=json.dumps(
            structured_data,
            sort_keys=True,
            separators=(",", ":"),
        ),
        structured_data=structured_data,
        provenance=EvidenceProvenance(
            source_type=EvidenceSourceType.TOOL_RESULT,
            tool_name="run_terminal",
            attempt=2,
        ),
        resource_refs=[
            "agents/terminal/runtime_graph.py",
        ],
    )


def test_builder_creates_search_document():
    builder = (
        DeterministicSearchDocumentBuilder()
    )

    evidence = make_evidence()

    document = builder.build(
        thread_id="thread-a",
        evidence=evidence,
    )

    assert document.evidence_id == (
        "evidence-1"
    )

    assert document.chunk_id == "0"

    assert document.thread_id == (
        "thread-a"
    )

    assert (
        "agents/terminal/runtime_graph.py"
        in document.text
    )

    assert (
        "The runtime uses concurrent execution."
        in document.text
    )

    assert (
        "runtime output"
        in document.text
    )


def test_document_id_is_stable():
    builder = (
        DeterministicSearchDocumentBuilder()
    )

    evidence = make_evidence()

    first = builder.build(
        thread_id="thread-a",
        evidence=evidence,
    )

    second = builder.build(
        thread_id="thread-a",
        evidence=evidence,
    )

    assert first.document_id == (
        second.document_id
    )


def test_document_id_is_thread_scoped():
    builder = (
        DeterministicSearchDocumentBuilder()
    )

    evidence = make_evidence()

    thread_a = builder.build(
        thread_id="thread-a",
        evidence=evidence,
    )

    thread_b = builder.build(
        thread_id="thread-b",
        evidence=evidence,
    )

    assert (
        thread_a.document_id
        != thread_b.document_id
    )


def test_builder_preserves_non_json_content():
    builder = (
        DeterministicSearchDocumentBuilder()
    )

    evidence = EvidenceRecord(
        evidence_id="evidence-raw",
        content="The executor delegates work to the coordinator.",
        provenance=EvidenceProvenance(
            tool_name="read_file",
            attempt=1,
        ),
        resource_refs=[
            "agents/terminal/runtime/executor.py",
        ],
    )

    document = builder.build(
        thread_id="thread-a",
        evidence=evidence,
    )

    assert (
        "The executor delegates work "
        "to the coordinator."
        in document.text
    )