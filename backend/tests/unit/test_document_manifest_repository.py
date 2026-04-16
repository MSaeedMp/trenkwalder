import json
import tempfile
from pathlib import Path

import pytest

from app.repositories import DocumentManifestRepository

MANIFEST = [
    {
        "doc_id": "benefits.md",
        "path": "benefits.md",
        "format": "md",
        "title": "benefits",
        "num_chunks": 5,
        "ingested_at": "2026-01-01T00:00:00Z",
    },
    {
        "doc_id": "handbook.pdf",
        "path": "handbook.pdf",
        "format": "pdf",
        "title": "handbook",
        "num_chunks": 12,
        "ingested_at": "2026-01-01T00:00:00Z",
    },
]


@pytest.fixture
def repo() -> DocumentManifestRepository:
    tmpdir = tempfile.mkdtemp()
    path = Path(tmpdir) / "manifest.json"
    path.write_text(json.dumps(MANIFEST))
    return DocumentManifestRepository(str(path))


@pytest.mark.unit
def test_list_documents(repo: DocumentManifestRepository) -> None:
    docs = repo.list_documents()
    assert len(docs) == 2
    assert docs[0].doc_id == "benefits.md"
    assert docs[1].num_chunks == 12


@pytest.mark.unit
def test_get_existing(repo: DocumentManifestRepository) -> None:
    doc = repo.get("handbook.pdf")
    assert doc is not None
    assert doc.format == "pdf"
    assert doc.num_chunks == 12


@pytest.mark.unit
def test_get_missing(repo: DocumentManifestRepository) -> None:
    assert repo.get("nonexistent.txt") is None


@pytest.mark.unit
def test_refresh(repo: DocumentManifestRepository) -> None:
    assert len(repo.list_documents()) == 2
    repo.refresh()
    assert len(repo.list_documents()) == 2


@pytest.mark.unit
def test_missing_file_returns_empty() -> None:
    repo = DocumentManifestRepository("/nonexistent/path/manifest.json")
    assert repo.list_documents() == []
