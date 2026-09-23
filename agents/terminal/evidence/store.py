from agents.terminal.evidence.models import EvidenceRecord


class InMemoryEvidenceStore:
    """
    In-memory implementation of EvidenceStore.

    """

    def __init__(self) -> None:
        self._evidence: dict[str, EvidenceRecord] = {}

    async def add(
        self,
        evidence: EvidenceRecord,
    ) -> None:
        self._evidence[evidence.evidence_id] = evidence

    async def get(
        self,
        evidence_id: str,
    ) -> EvidenceRecord | None:
        return self._evidence.get(evidence_id)

    async def list(
        self,
        *,
        resource_ref: str | None = None,
        tool_name: str | None = None,
        limit: int = 100,
    ) -> list[EvidenceRecord]:

        results: list[EvidenceRecord] = []

        for evidence in self._evidence.values():

            if (
                resource_ref is not None
                and resource_ref not in evidence.resource_refs
            ):
                continue

            if (
                tool_name is not None
                and evidence.provenance.tool_name != tool_name
            ):
                continue

            results.append(evidence)

            if len(results) >= limit:
                break

        return results