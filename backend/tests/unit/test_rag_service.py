import pytest

from app.models import Chunk
from app.services import RAGService


class FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeVectorRepo:
    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[Chunk]:
        results = self._chunks
        if source_filter:
            results = [c for c in results if c.source == source_filter]
        return results[:top_k]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_returns_chunk_results() -> None:
    chunks = [
        Chunk(
            id="a:0:0", text="hello world", source="doc.md", format="md", page=1, section="Intro"
        ),
        Chunk(id="b:0:0", text="goodbye", source="doc.md", format="md", page=2, section="Outro"),
    ]
    svc = RAGService(embedder=FakeEmbedder(), vector_repo=FakeVectorRepo(chunks))  # type: ignore[arg-type]
    results = await svc.search("hello")
    assert len(results) == 2
    assert results[0].text == "hello world"
    assert results[0].source == "doc.md"
    assert results[0].section == "Intro"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_with_source_filter() -> None:
    chunks = [
        Chunk(id="a:0:0", text="from handbook", source="handbook.pdf", format="pdf"),
        Chunk(id="b:0:0", text="from benefits", source="benefits.md", format="md"),
    ]
    svc = RAGService(embedder=FakeEmbedder(), vector_repo=FakeVectorRepo(chunks))  # type: ignore[arg-type]
    results = await svc.search("test", source_filter="handbook.pdf")
    assert len(results) == 1
    assert results[0].source == "handbook.pdf"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_respects_top_k() -> None:
    chunks = [
        Chunk(id=f"c:{i}:0", text=f"chunk {i}", source="doc.md", format="md") for i in range(10)
    ]
    svc = RAGService(embedder=FakeEmbedder(), vector_repo=FakeVectorRepo(chunks))  # type: ignore[arg-type]
    results = await svc.search("test", top_k=3)
    assert len(results) == 3
