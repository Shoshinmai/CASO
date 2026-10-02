import math
import os

import pytest

from agents.terminal.retrieval.embedding import (
    Qwen3EmbeddingConfig,
    Qwen3EmbeddingProvider,
)
from agents.terminal.retrieval.models import (
    SearchDocument,
)


RUN_REAL_QWEN = (
    os.getenv(
        "RUN_REAL_QWEN_SMOKE",
        "",
    ).lower()
    in {
        "1",
        "true",
        "yes",
    }
)


def cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    dot = sum(
        a * b
        for a, b in zip(
            left,
            right,
        )
    )

    left_norm = math.sqrt(
        sum(
            value * value
            for value in left
        )
    )

    right_norm = math.sqrt(
        sum(
            value * value
            for value in right
        )
    )

    return dot / (
        left_norm * right_norm
    )


@pytest.mark.skipif(
    not RUN_REAL_QWEN,
    reason=(
        "Set RUN_REAL_QWEN_SMOKE=1 to run "
        "the real Ollama Qwen embedding smoke test."
    ),
)
@pytest.mark.asyncio
async def test_real_qwen_ollama_embedding():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            model_name=(
                "qwen3-embedding:4b"
            ),
            dimension=1024,
            batch_size=2,
            host=(
                "http://127.0.0.1:11434"
            ),
            normalize_embeddings=True,
        ),
    )

    documents = [
        SearchDocument(
            document_id="doc-runtime",
            evidence_id="evidence-runtime",
            chunk_id="0",
            thread_id="smoke-thread",
            text=(
                "The runtime memory update node "
                "applies the RuntimeProcessingResult "
                "to ActiveTaskMemory."
            ),
            resource_refs=[
                "agents/terminal/runtime/nodes.py",
            ],
            tool_name="run_terminal",
        ),
        SearchDocument(
            document_id="doc-unrelated",
            evidence_id="evidence-unrelated",
            chunk_id="0",
            thread_id="smoke-thread",
            text=(
                "The application stores database "
                "connection settings and migration metadata."
            ),
            resource_refs=[
                "database/config.py",
            ],
            tool_name="read_file",
        ),
    ]

    document_vectors = (
        await provider.embed_documents(
            [
                document.text
                for document in documents
            ],
        )
    )

    query_vectors = (
        await provider.embed_queries(
            [
                (
                    "Where is the runtime memory "
                    "update applied?"
                ),
            ],
        )
    )

    assert len(document_vectors) == 2
    assert len(query_vectors) == 1

    assert all(
        len(vector) == provider.dimension
        for vector in document_vectors
    )

    assert len(
        query_vectors[0],
    ) == provider.dimension

    for vector in (
        *document_vectors,
        query_vectors[0],
    ):
        assert all(
            math.isfinite(value)
            for value in vector
        )

        norm = math.sqrt(
            sum(
                value * value
                for value in vector
            )
        )

        assert norm == pytest.approx(
            1.0,
            abs=1e-3,
        )

    relevant_similarity = cosine_similarity(
        query_vectors[0],
        document_vectors[0],
    )

    unrelated_similarity = cosine_similarity(
        query_vectors[0],
        document_vectors[1],
    )

    print(
        "relevant_similarity=",
        relevant_similarity,
    )

    print(
        "unrelated_similarity=",
        unrelated_similarity,
    )

    assert (
        relevant_similarity
        > unrelated_similarity
    )