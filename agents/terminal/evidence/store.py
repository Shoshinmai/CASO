from typing import Protocol

from agents.terminal.evidence.models import (
    EvidenceRecord,
)


class EvidenceStore(Protocol):
    """
    Thread-scoped contract for retained evidence.
    """

    async def add(
        self,
        thread_id: str,
        evidence: EvidenceRecord,
    ) -> None: ...

    async def get(
        self,
        thread_id: str,
        evidence_id: str,
    ) -> EvidenceRecord | None: ...

    async def list(
        self,
        thread_id: str,
        *,
        resource_ref: str | None = None,
        tool_name: str | None = None,
        limit: int = 100,
    ) -> list[EvidenceRecord]: ...


class InMemoryEvidenceStore:
    """
    Process-local, thread-scoped evidence store.

    Evidence is isolated by LangGraph thread_id.
    """

    def __init__(self) -> None:
        self._evidence: dict[
            str,
            dict[str, EvidenceRecord],
        ] = {}

    async def add(
        self,
        thread_id: str,
        evidence: EvidenceRecord,
    ) -> None:
        thread_evidence = self._evidence.setdefault(
            thread_id,
            {},
        )

        thread_evidence[evidence.evidence_id] = evidence

    async def get(
        self,
        thread_id: str,
        evidence_id: str,
    ) -> EvidenceRecord | None:
        thread_evidence = self._evidence.get(
            thread_id,
            {},
        )

        return thread_evidence.get(
            evidence_id,
        )

    async def list(
        self,
        thread_id: str,
        *,
        resource_ref: str | None = None,
        tool_name: str | None = None,
        limit: int = 100,
    ) -> list[EvidenceRecord]:

        thread_evidence = self._evidence.get(
            thread_id,
            {},
        )

        results: list[EvidenceRecord] = []

        for evidence in thread_evidence.values():

            if resource_ref is not None and resource_ref not in evidence.resource_refs:
                continue

            if tool_name is not None and evidence.provenance.tool_name != tool_name:
                continue

            results.append(
                evidence,
            )

            if len(results) >= limit:
                break

        return results
