import tempfile

import pytest

from app.models import Chunk
from app.repositories import LanceDBVectorRepository


def _chunk(id: str, source: str, vector: list[float]) -> Chunk:
    return Chunk(id=id, text=f"text {id}", vector=vector, source=source, format="md")


@pytest.mark.integration
def test_upsert_search_and_filter() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LanceDBVectorRepository.open(tmpdir)
        repo.upsert(
            [
                _chunk("a", "handbook.pdf", [1.0, 0.0, 0.0]),
                _chunk("b", "handbook.pdf", [0.0, 1.0, 0.0]),
                _chunk("c", "benefits.md", [0.0, 0.0, 1.0]),
            ]
        )

        results = repo.search([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].id == "a"

        filtered = repo.search([1.0, 0.0, 0.0], top_k=10, source_filter="handbook.pdf")
        assert all(r.source == "handbook.pdf" for r in filtered)
