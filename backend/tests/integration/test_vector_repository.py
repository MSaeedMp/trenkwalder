import tempfile

import pytest

from app.models import Chunk
from app.repositories import LanceDBVectorRepository


def _make_chunk(id: str, source: str, vector: list[float]) -> Chunk:
    return Chunk(
        id=id,
        text=f"text for {id}",
        vector=vector,
        source=source,
        format="md",
        page=1,
        section="test",
        heading_path=["Test"],
        char_start=0,
        char_end=10,
    )


@pytest.mark.integration
def test_upsert_and_search() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LanceDBVectorRepository.open(tmpdir)

        # 3-dimensional vectors for simplicity
        chunks = [
            _make_chunk("a", "doc1.md", [1.0, 0.0, 0.0]),
            _make_chunk("b", "doc1.md", [0.0, 1.0, 0.0]),
            _make_chunk("c", "doc2.md", [0.0, 0.0, 1.0]),
        ]
        repo.upsert(chunks)

        # Search near [1, 0, 0] — should return "a" first
        results = repo.search([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].id == "a"


@pytest.mark.integration
def test_source_filter() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LanceDBVectorRepository.open(tmpdir)

        chunks = [
            _make_chunk("a", "handbook.pdf", [1.0, 0.0, 0.0]),
            _make_chunk("b", "handbook.pdf", [0.9, 0.1, 0.0]),
            _make_chunk("c", "benefits.md", [0.8, 0.2, 0.0]),
        ]
        repo.upsert(chunks)

        # Without filter: all 3 returned
        all_results = repo.search([1.0, 0.0, 0.0], top_k=10)
        assert len(all_results) == 3

        # With filter: only handbook chunks
        filtered = repo.search([1.0, 0.0, 0.0], top_k=10, source_filter="handbook.pdf")
        assert len(filtered) == 2
        assert all(r.source == "handbook.pdf" for r in filtered)


@pytest.mark.integration
def test_search_on_empty_returns_empty() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LanceDBVectorRepository.open(tmpdir)
        results = repo.search([1.0, 0.0, 0.0], top_k=5)
        assert results == []


@pytest.mark.integration
def test_upsert_multiple_batches() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LanceDBVectorRepository.open(tmpdir)

        repo.upsert([_make_chunk("a", "doc.md", [1.0, 0.0, 0.0])])
        repo.upsert([_make_chunk("b", "doc.md", [0.0, 1.0, 0.0])])

        results = repo.search([0.5, 0.5, 0.0], top_k=10)
        assert len(results) == 2


@pytest.mark.integration
def test_open_reopens_existing() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        repo1 = LanceDBVectorRepository.open(tmpdir)
        repo1.upsert([_make_chunk("a", "doc.md", [1.0, 0.0, 0.0])])

        repo2 = LanceDBVectorRepository.open(tmpdir)
        results = repo2.search([1.0, 0.0, 0.0], top_k=5)
        assert len(results) == 1
        assert results[0].id == "a"
