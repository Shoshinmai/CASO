import pytest
from pydantic import ValidationError

from agents.terminal.retrieval.models import (
    DenseSearchHit,
)


def test_dense_search_hit_contains_only_index_result_data():
    hit = DenseSearchHit(
        document_id="doc-17",
        score=0.91,
        rank=1,
    )

    assert hit.document_id == "doc-17"
    assert hit.score == 0.91
    assert hit.rank == 1


def test_dense_search_hit_requires_document_id():
    with pytest.raises(ValidationError):
        DenseSearchHit(
            document_id="",
            score=0.91,
            rank=1,
        )


def test_dense_search_hit_requires_positive_rank():
    with pytest.raises(ValidationError):
        DenseSearchHit(
            document_id="doc-17",
            score=0.91,
            rank=0,
        )


def test_dense_search_hit_is_independent_of_evidence_record():
    hit = DenseSearchHit(
        document_id="doc-17",
        score=0.91,
        rank=1,
    )

    assert not hasattr(
        hit,
        "evidence",
    )