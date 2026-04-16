import lancedb

from app.core.config import Settings
from app.core.observability import get_logger
from etl.structured.pipeline import run_structured
from etl.unstructured.pipeline import run_unstructured

logger = get_logger(__name__)


def run_all_pipelines(settings: Settings, db: lancedb.DBConnection) -> None:
    """Run all ETL pipelines. Skip tables that already have data."""
    existing = set(db.list_tables().tables)

    if "employees" not in existing:
        run_structured(settings.docs_dir, db)
    else:
        logger.info("structured_skipped", reason="employees table already exists")

    if "chunks" not in existing:
        run_unstructured(
            docs_dir=settings.docs_dir,
            vector_store_path=settings.vector_store_path,
            db=db,
            embedding_provider=settings.embedding_provider,
            gemini_api_key=settings.gemini_api_key,
            gemini_embedding_model=settings.gemini_embedding_model,
        )
    else:
        logger.info("unstructured_skipped", reason="chunks table already exists")
