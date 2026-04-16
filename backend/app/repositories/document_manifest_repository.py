import json
from pathlib import Path

from app.core.observability import get_logger
from app.schemas.rag import DocumentMetadata

logger = get_logger(__name__)


class DocumentManifestRepository:
    """Read-only access to the ingestion manifest.json."""

    def __init__(self, manifest_path: str) -> None:
        self._path = Path(manifest_path)
        self._docs: list[DocumentMetadata] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._docs = []
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._docs = [DocumentMetadata(**item) for item in raw]
        logger.info("manifest_loaded", count=len(self._docs))

    def list_documents(self) -> list[DocumentMetadata]:
        return list(self._docs)

    def get(self, doc_id: str) -> DocumentMetadata | None:
        for doc in self._docs:
            if doc.doc_id == doc_id:
                return doc
        return None

    def refresh(self) -> None:
        """Reload the manifest from disk."""
        self._load()
