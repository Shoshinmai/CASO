from typing import Any

from pydantic import BaseModel, Field

from agents.terminal.evidence.models import (
    EvidenceRecord,
    EvidenceRetrievalQuery,
)


class RetrievedEvidence(BaseModel):
    """
    One ranked evidence item returned by the retrieval subsystem.

    The authoritative evidence remains the EvidenceRecord.
    This model carries retrieval-specific metadata only.
    """

    evidence: EvidenceRecord

    score: float

    rank: int = Field(
        ge=1,
    )

    source: str = Field(
        min_length=1,
    )


class SearchDocument(BaseModel):
    """
    Derived searchable representation of an EvidenceRecord.

    SearchDocument is not authoritative storage. It exists so retrieval
    implementations can build semantic and lexical indexes without
    coupling those indexes directly to EvidenceRecord.
    """

    document_id: str = Field(
        min_length=1,
    )

    evidence_id: str = Field(
        min_length=1,
    )

    text: str = Field(
        min_length=1,
    )

    thread_id: str = Field(
        min_length=1,
    )

    resource_refs: list[str] = Field(
        default_factory=list,
    )

    tool_name: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class EvidenceRetrievalResult(BaseModel):
    """
    Public result returned by an EvidenceRetriever.

    This intentionally wraps ranked retrieval results rather than
    returning bare EvidenceRecord instances.
    """

    query: EvidenceRetrievalQuery

    results: list[RetrievedEvidence] = Field(
        default_factory=list,
    )

    total_candidates: int = Field(
        default=0,
        ge=0,
    )