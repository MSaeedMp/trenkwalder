import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import lancedb

from app.models import Chunk
from app.schemas.rag import DocumentMetadata


def write_chunks(db: lancedb.DBConnection, chunks: list[Chunk]) -> None:
    """Write embedded chunks to the LanceDB chunks table."""
    if not chunks:
        return
    records = [asdict(c) for c in chunks]
    db.create_table("chunks", data=records, mode="overwrite")  # type: ignore[reportUnknownMemberType]


def write_manifest(store_path: str, chunks: list[Chunk]) -> None:
    """Write a manifest.json summarizing what was ingested."""
    docs: dict[str, DocumentMetadata] = {}
    for chunk in chunks:
        if chunk.source not in docs:
            docs[chunk.source] = DocumentMetadata(
                doc_id=chunk.source,
                path=chunk.source,
                format=chunk.format,
                title=chunk.source.rsplit(".", 1)[0],
                num_chunks=0,
                ingested_at=datetime.now(UTC).isoformat(),
            )
        docs[chunk.source].num_chunks += 1

    manifest_path = Path(store_path) / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps([d.model_dump() for d in docs.values()], indent=2),
        encoding="utf-8",
    )
