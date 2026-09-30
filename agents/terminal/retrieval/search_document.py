import hashlib
import json
from typing import Any

from agents.terminal.evidence.models import EvidenceRecord

from .models import SearchDocument


class DeterministicSearchDocumentBuilder:
    """
    Deterministically converts retained EvidenceRecord objects into
    retrieval-oriented SearchDocuments.

    The builder does not:
    - call an LLM,
    - generate embeddings,
    - access an index,
    - mutate EvidenceRecord.
    """

    def build(
        self,
        *,
        thread_id: str,
        evidence: EvidenceRecord,
    ) -> SearchDocument:
        if not thread_id:
            raise ValueError("thread_id cannot be empty.")

        text = self._build_search_text(
            evidence,
        )

        if not text.strip():
            raise ValueError(
                "Evidence does not contain searchable content."
            )

        chunk_id = "0"

        document_id = self._build_document_id(
            thread_id=thread_id,
            evidence_id=evidence.evidence_id,
            chunk_id=chunk_id,
        )

        metadata = self._build_metadata(
            evidence,
        )

        return SearchDocument(
            document_id=document_id,
            evidence_id=evidence.evidence_id,
            chunk_id=chunk_id,
            text=text,
            thread_id=thread_id,
            resource_refs=list(evidence.resource_refs),
            tool_name=evidence.provenance.tool_name,
            metadata=metadata,
        )

    @staticmethod
    def _build_document_id(
        *,
        thread_id: str,
        evidence_id: str,
        chunk_id: str,
    ) -> str:
        canonical = (
            f"{thread_id}:"
            f"{evidence_id}:"
            f"{chunk_id}"
        )

        return hashlib.sha256(
            canonical.encode("utf-8"),
        ).hexdigest()

    @staticmethod
    def _build_metadata(
        evidence: EvidenceRecord,
    ) -> dict[str, Any]:
        provenance = evidence.provenance

        return {
            "source_type": provenance.source_type.value,
            "attempt": provenance.attempt,
            "source_identifier": provenance.source_identifier,
            "artifact_ref": evidence.artifact_ref,
            "provenance_metadata": dict(
                provenance.metadata,
            ),
        }

    def _build_search_text(
        self,
        evidence: EvidenceRecord,
    ) -> str:
        sections: list[str] = []

        if evidence.resource_refs:
            sections.append(
                self._format_resource_refs(
                    evidence.resource_refs,
                )
            )

        sections.append(
            f"Source Tool:\n{evidence.provenance.tool_name}"
        )

        structured = evidence.structured_data

        if self._is_canonical_structured_content(
            evidence.content,
            structured,
        ):
            structured_text = (
                self._format_structured_data(
                    structured,
                )
            )

            if structured_text:
                sections.append(
                    structured_text,
                )
        else:
            content = evidence.content.strip()

            if content:
                sections.append(
                    f"Evidence:\n{content}",
                )

        return "\n\n".join(
            section
            for section in sections
            if section.strip()
        )

    @staticmethod
    def _is_canonical_structured_content(
        content: str,
        structured_data: dict[str, Any],
    ) -> bool:
        try:
            parsed = json.loads(content)
        except (TypeError, ValueError):
            return False

        return parsed == structured_data

    def _format_structured_data(
        self,
        data: dict[str, Any],
    ) -> str:
        sections: list[str] = []

        self._append_facts(
            sections,
            data.get("facts"),
        )

        self._append_resources(
            sections,
            data.get("resources"),
        )

        self._append_execution(
            sections,
            data.get("execution"),
        )

        self._append_artifact(
            sections,
            data.get("artifact"),
        )

        return "\n\n".join(
            sections,
        )

    @staticmethod
    def _format_resource_refs(
        resource_refs: list[str],
    ) -> str:
        lines = [
            "Resources:",
        ]

        lines.extend(
            f"- {resource}"
            for resource in resource_refs
            if resource.strip()
        )

        return "\n".join(lines)

    @staticmethod
    def _append_facts(
        sections: list[str],
        facts: Any,
    ) -> None:
        if not isinstance(facts, list):
            return

        lines: list[str] = [
            "Facts:",
        ]

        for fact in facts:
            if not isinstance(fact, dict):
                continue

            statement = str(
                fact.get(
                    "statement",
                    "",
                )
            ).strip()

            source = str(
                fact.get(
                    "source",
                    "",
                )
            ).strip()

            if not statement:
                continue

            if source:
                lines.append(
                    f"- {statement} (source: {source})",
                )
            else:
                lines.append(
                    f"- {statement}",
                )

        if len(lines) > 1:
            sections.append(
                "\n".join(lines),
            )

    @staticmethod
    def _append_resources(
        sections: list[str],
        resources: Any,
    ) -> None:
        if not isinstance(resources, list):
            return

        lines: list[str] = [
            "Discovered Resources:",
        ]

        for resource in resources:
            if not isinstance(resource, dict):
                continue

            resource_type = str(
                resource.get(
                    "type",
                    "",
                )
            ).strip()

            identifier = str(
                resource.get(
                    "identifier",
                    "",
                )
            ).strip()

            if not identifier:
                continue

            if resource_type:
                lines.append(
                    f"- {resource_type}: {identifier}",
                )
            else:
                lines.append(
                    f"- {identifier}",
                )

        if len(lines) > 1:
            sections.append(
                "\n".join(lines),
            )

    @staticmethod
    def _append_execution(
        sections: list[str],
        execution: Any,
    ) -> None:
        if not isinstance(execution, dict):
            return

        lines: list[str] = [
            "Execution:",
        ]

        ordered_fields = (
            "success",
            "progress_made",
            "message",
            "return_code",
            "stdout",
            "stderr",
        )

        for field_name in ordered_fields:
            if field_name not in execution:
                continue

            value = execution[field_name]

            if value in (
                None,
                "",
            ):
                continue

            label = field_name.replace(
                "_",
                " ",
            ).title()

            lines.append(
                f"{label}: {value}",
            )

        if len(lines) > 1:
            sections.append(
                "\n".join(lines),
            )

    @staticmethod
    def _append_artifact(
        sections: list[str],
        artifact: Any,
    ) -> None:
        if not isinstance(artifact, dict):
            return

        artifact_type = str(
            artifact.get(
                "artifact_type",
                "",
            )
        ).strip()

        summary = str(
            artifact.get(
                "summary",
                "",
            )
        ).strip()

        lines = [
            "Artifact:",
        ]

        if artifact_type:
            lines.append(
                f"Type: {artifact_type}",
            )

        if summary:
            lines.append(
                f"Summary: {summary}",
            )

        if len(lines) > 1:
            sections.append(
                "\n".join(lines),
            )