import lancedb

from app.core.observability import get_logger
from app.models import Chunk
from pipelines.unstructured.extract import load_documents
from pipelines.unstructured.load import write_chunks, write_manifest
from pipelines.unstructured.transform import (
    EmbeddingProvider,
    GeminiEmbeddingProvider,
    chunk_document,
    embed_chunks,
)

logger = get_logger(__name__)


def _build_embedding_provider(
    provider_name: str,
    api_key: str,
    model: str,
) -> EmbeddingProvider:
    if provider_name == "gemini":
        return GeminiEmbeddingProvider(api_key=api_key, model=model)
    msg = f"Unknown embedding provider: {provider_name!r}"
    raise ValueError(msg)


def run_unstructured(
    docs_dir: str,
    vector_store_path: str,
    db: lancedb.DBConnection,
    embedding_provider: str,
    gemini_api_key: str,
    gemini_embedding_model: str,
) -> None:
    """Run the unstructured ETL pipeline: docs → chunk → embed → LanceDB."""
    logger.info("unstructured_started", docs_dir=docs_dir)

    if embedding_provider == "gemini" and not gemini_api_key:
        logger.warning("unstructured_skipped", reason="missing Gemini API key")
        return

    raw_docs = load_documents(docs_dir)
    if not raw_docs:
        logger.warning("unstructured_skipped", reason="no documents found")
        return

    logger.info("documents_parsed", count=len(raw_docs))

    all_chunks: list[Chunk] = []
    for doc in raw_docs:
        doc_chunks = chunk_document(doc)
        all_chunks.extend(doc_chunks)

    logger.info("chunks_created", count=len(all_chunks))

    provider = _build_embedding_provider(embedding_provider, gemini_api_key, gemini_embedding_model)
    embedded = embed_chunks(all_chunks, provider)

    write_chunks(db, embedded)
    write_manifest(vector_store_path, embedded)

    logger.info("unstructured_completed", chunks_loaded=len(embedded))
