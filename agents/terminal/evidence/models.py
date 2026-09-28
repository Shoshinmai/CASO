from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceSourceType(StrEnum):
    TOOL_RESULT = "tool_result"
    FILE = "file"
    TERMINAL = "terminal"
    ARTIFACT = "artifact"
    OTHER = "other"


class EvidenceProvenance(BaseModel):
    """
    Provenance describing where an evidence record came from.
    """

    source_type: EvidenceSourceType = EvidenceSourceType.TOOL_RESULT

    tool_name: str

    attempt: int = Field(default=1, ge=1)

    source_identifier: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceRecord(BaseModel):
    """
    Durable representation of information directly observed during execution.

    Evidence is intentionally descriptive rather than interpretive. Higher
    layers may derive findings or understanding from it.
    """

    evidence_id: str

    content: str

    structured_data: dict[str, Any] = Field(default_factory=dict)

    provenance: EvidenceProvenance

    resource_refs: list[str] = Field(default_factory=list)

    artifact_ref: str | None = None

class EvidenceRetrievalQuery(BaseModel):
    """
    Describes an information request against retained evidence.

    `query` represents the semantic information need.

    The remaining fields are deterministic constraints that can be
    applied before retrieval ranking.
    """

    query: str = Field(
        min_length=1,
    )

    resource_refs: list[str] = Field(
        default_factory=list,
    )

    tool_name: str | None = None

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )