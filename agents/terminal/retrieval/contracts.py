from typing import Protocol

from agents.terminal.evidence.models import (
    EvidenceRecord,
    EvidenceRetrievalQuery,
)

from .models import (
    EvidenceRetrievalResult,
    RetrievedEvidence,
    SearchDocument,
)


class SearchDocumentBuilder(Protocol):
    """
    Converts authoritative EvidenceRecord objects into retrieval-oriented
    SearchDocument objects.
    """

    def build(
        self,
        *,
        thread_id: str,
        evidence: EvidenceRecord,
    ) -> SearchDocument:
        ...


class EmbeddingProvider(Protocol):
    """
    Provider-agnostic embedding boundary.
    """

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...


class DenseIndex(Protocol):
    """
    Provider-agnostic dense/vector index.
    """

    async def upsert(
        self,
        *,
        documents: list[SearchDocument],
        vectors: list[list[float]],
    ) -> None:
        ...

    async def search(
        self,
        *,
        thread_id: str,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedEvidence]:
        ...


class LexicalIndex(Protocol):
    """
    Provider-agnostic lexical index.

    The initial implementation is expected to use BM25.
    """

    async def upsert(
        self,
        *,
        documents: list[SearchDocument],
    ) -> None:
        ...

    async def search(
        self,
        *,
        thread_id: str,
        query: str,
        limit: int,
    ) -> list[RetrievedEvidence]:
        ...


class EvidenceRetriever(Protocol):
    """
    Public retrieval boundary exposed to higher-level Terminal Agent logic.

    The implementation may combine dense, lexical, fusion, reranking,
    or future retrieval mechanisms without leaking those details here.
    """

    async def retrieve(
        self,
        *,
        thread_id: str,
        query: EvidenceRetrievalQuery,
    ) -> EvidenceRetrievalResult:
        ...