from typing import Any

from app.core.observability import get_logger
from app.models import Chunk
from app.repositories.vector_repository import LanceDBVectorRepository
from app.schemas.rag import ChunkResult

logger = get_logger(__name__)


def _chunk_to_result(chunk: Chunk) -> ChunkResult:
    return ChunkResult(
        text=chunk.text,
        source=chunk.source,
        page=chunk.page,
        section=chunk.section,
    )


class RAGService:
    """Embed queries and retrieve relevant document chunks."""

    def __init__(self, embedder: Any, vector_repo: LanceDBVectorRepository) -> None:
        self._embedder = embedder
        self._vector_repo = vector_repo

    async def search(
        self,
        query: str,
        source_filter: str | None = None,
        top_k: int = 5,
    ) -> list[ChunkResult]:
        """Return top-k chunks matching the query."""
        vectors: list[list[float]] = self._embedder.embed([query])
        query_vector = vectors[0]
        chunks = self._vector_repo.search(query_vector, top_k=top_k, source_filter=source_filter)
        results = [_chunk_to_result(c) for c in chunks]
        logger.info("rag_search", query_len=len(query), top_k=top_k, results=len(results))
        return results
