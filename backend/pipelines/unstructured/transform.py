from dataclasses import replace
from pathlib import Path
from typing import Any, Protocol, cast

import tiktoken

from app.models import Chunk
from app.schemas.rag import RawDocument

_ENCODER = tiktoken.get_encoding("cl100k_base")
_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50


def chunk_document(doc: RawDocument) -> list[Chunk]:
    """Split a RawDocument into ~500-token chunks with 50-token overlap."""
    source = Path(doc.path).name
    chunks: list[Chunk] = []
    chunk_idx = 0

    for page in doc.pages:
        text = page.text
        if not text.strip():
            continue

        tokens = _ENCODER.encode(text)
        start = 0

        while start < len(tokens):
            end = min(start + _CHUNK_SIZE, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = _ENCODER.decode(chunk_tokens)

            char_start = text.find(chunk_text[:20]) if len(chunk_text) >= 20 else 0
            char_end = char_start + len(chunk_text) if char_start >= 0 else len(chunk_text)

            section = page.heading_path[-1] if page.heading_path else ""

            chunks.append(
                Chunk(
                    id=f"{source}:{page.page}:{chunk_idx}",
                    text=chunk_text,
                    source=source,
                    format=doc.format,
                    page=page.page,
                    section=section,
                    heading_path=list(page.heading_path),
                    char_start=max(char_start, 0),
                    char_end=char_end,
                )
            )
            chunk_idx += 1

            if end >= len(tokens):
                break
            start = end - _CHUNK_OVERLAP

    return chunks


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class GeminiEmbeddingProvider:
    """Embed text using Google's Gemini embedding model."""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001") -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        result = self._client.models.embed_content(  # type: ignore[reportUnknownMemberType]
            model=self._model,
            contents=cast(Any, texts),
        )
        vectors: list[list[float]] = []
        for e in result.embeddings or []:
            if e.values is not None:
                vectors.append(list(e.values))
            else:
                vectors.append([])
        return vectors


def embed_chunks(chunks: list[Chunk], provider: EmbeddingProvider) -> list[Chunk]:
    """Attach embedding vectors to chunks."""
    if not chunks:
        return chunks

    texts = [c.text for c in chunks]
    # Batch in groups of 100 to avoid API limits
    batch_size = 100
    all_vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_vectors.extend(provider.embed(batch))

    embedded: list[Chunk] = []
    for chunk, vector in zip(chunks, all_vectors, strict=True):
        embedded.append(replace(chunk, vector=vector))
    return embedded
