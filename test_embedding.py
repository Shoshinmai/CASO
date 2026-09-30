import numpy as np
import pytest

from agents.terminal.retrieval.embedding import (
    EmbeddingProviderError,
    Qwen3EmbeddingConfig,
    Qwen3EmbeddingProvider,
)


class FakeEmbeddingModel:
    def __init__(
        self,
        dimension: int,
    ) -> None:
        self.dimension = dimension

    def encode_document(
        self,
        texts,
        **kwargs,
    ):
        return np.ones(
            (
                len(texts),
                self.dimension,
            ),
            dtype=np.float32,
        )

    def encode_query(
        self,
        texts,
        **kwargs,
    ):
        return np.full(
            (
                len(texts),
                self.dimension,
            ),
            2.0,
            dtype=np.float32,
        )


class BadCountModel:
    def encode_document(
        self,
        texts,
        **kwargs,
    ):
        return np.ones(
            (
                max(
                    0,
                    len(texts) - 1,
                ),
                4,
            ),
            dtype=np.float32,
        )

    def encode_query(
        self,
        texts,
        **kwargs,
    ):
        return np.ones(
            (
                len(texts),
                4,
            ),
            dtype=np.float32,
        )


class BadDimensionModel:
    def encode_document(
        self,
        texts,
        **kwargs,
    ):
        return np.ones(
            (
                len(texts),
                3,
            ),
            dtype=np.float32,
        )

    def encode_query(
        self,
        texts,
        **kwargs,
    ):
        return np.ones(
            (
                len(texts),
                3,
            ),
            dtype=np.float32,
        )


@pytest.mark.asyncio
async def test_document_embedding():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
            batch_size=2,
        ),
        model=FakeEmbeddingModel(
            dimension=4,
        ),
    )

    result = await provider.embed_documents(
        [
            "document one",
            "document two",
        ],
    )

    assert len(result) == 2
    assert len(result[0]) == 4
    assert result[0] == [1.0] * 4


@pytest.mark.asyncio
async def test_query_embedding():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
        ),
        model=FakeEmbeddingModel(
            dimension=4,
        ),
    )

    result = await provider.embed_queries(
        [
            "query one",
        ],
    )

    assert len(result) == 1
    assert len(result[0]) == 4
    assert result[0] == [2.0] * 4


@pytest.mark.asyncio
async def test_empty_batches_return_empty():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
        ),
        model=FakeEmbeddingModel(
            dimension=4,
        ),
    )

    assert (
        await provider.embed_documents([])
        == []
    )

    assert (
        await provider.embed_queries([])
        == []
    )


@pytest.mark.asyncio
async def test_empty_text_is_rejected():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
        ),
        model=FakeEmbeddingModel(
            dimension=4,
        ),
    )

    with pytest.raises(ValueError):
        await provider.embed_documents(
            ["valid", "   "],
        )


@pytest.mark.asyncio
async def test_vector_count_mismatch_is_rejected():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
        ),
        model=BadCountModel(),
    )

    with pytest.raises(EmbeddingProviderError):
        await provider.embed_documents(
            [
                "one",
                "two",
            ],
        )


@pytest.mark.asyncio
async def test_vector_dimension_mismatch_is_rejected():
    provider = Qwen3EmbeddingProvider(
        config=Qwen3EmbeddingConfig(
            dimension=4,
        ),
        model=BadDimensionModel(),
    )

    with pytest.raises(EmbeddingProviderError):
        await provider.embed_documents(
            ["one"],
        )