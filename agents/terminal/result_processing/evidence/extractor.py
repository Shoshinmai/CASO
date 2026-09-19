import hashlib
import json

from agents.terminal.result_processing.evidence.models import (
    EvidenceProvenance,
    EvidenceRecord,
    EvidenceSourceType,
)
from agents.terminal.result_processing.models import NormalizedResult


def extract_evidence(normalized: NormalizedResult) -> EvidenceRecord:
    """
    Convert a normalized tool result into the first durable information
    representation used by Prototype 3.

    This function only records observed information. It does not infer
    higher-level findings or mutate runtime state.
    """

    structured_data = {
        "facts": [
            {
                "statement": fact.statement,
                "source": fact.source,
            }
            for fact in normalized.facts
        ],
        "resources": [
            {
                "type": resource.type.value,
                "identifier": resource.identifier,
                "metadata": resource.metadata,
            }
            for resource in normalized.resources
        ],
        "execution": {
            "success": normalized.execution.success,
            "progress_made": normalized.execution.progress_made,
            "message": normalized.execution.message,
            "return_code": normalized.execution.return_code,
            "stdout": normalized.execution.stdout,
            "stderr": normalized.execution.stderr,
        },
    }

    if normalized.artifact is not None:
        structured_data["artifact"] = {
            "artifact_type": normalized.artifact.artifact_type,
            "summary": normalized.artifact.summary,
        }

    canonical = json.dumps(
        structured_data,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )

    evidence_id = hashlib.sha256(
        (
            f"{normalized.context.tool_name}:"
            f"{normalized.context.attempt}:"
            f"{canonical}"
        ).encode("utf-8")
    ).hexdigest()

    resource_refs = [
        resource.identifier
        for resource in normalized.resources
    ]

    return EvidenceRecord(
        evidence_id=evidence_id,
        content=canonical,
        structured_data=structured_data,
        provenance=EvidenceProvenance(
            source_type=EvidenceSourceType.TOOL_RESULT,
            tool_name=normalized.context.tool_name,
            attempt=normalized.context.attempt,
        ),
        resource_refs=resource_refs,
    )
