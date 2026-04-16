from dataclasses import asdict
from typing import Any, cast

import lancedb

from app.core.observability import get_logger
from app.models import Chunk

logger = get_logger(__name__)


def _row_to_chunk(row: dict[str, Any]) -> Chunk:
    return Chunk(
        id=str(row.get("id", "")),
        text=str(row.get("text", "")),
        vector=list(row.get("vector", [])),
        source=str(row.get("source", "")),
        format=str(row.get("format", "")),
        page=int(row.get("page", 0)),
        section=str(row.get("section", "")),
        heading_path=list(row.get("heading_path", [])),
        char_start=int(row.get("char_start", 0)),
        char_end=int(row.get("char_end", 0)),
    )


class LanceDBVectorRepository:
    """Thin wrapper over a LanceDB `chunks` table."""

    def __init__(self, db: lancedb.DBConnection) -> None:
        self._db = db
        self._table_name = "chunks"

    @classmethod
    def open(cls, path: str) -> "LanceDBVectorRepository":
        db = lancedb.connect(path)
        return cls(db)

    def _has_table(self) -> bool:
        return self._table_name in self._db.list_tables().tables

    def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        records = [asdict(c) for c in chunks]
        if self._has_table():
            table = self._db.open_table(self._table_name)
            table.add(records)  # type: ignore[reportUnknownMemberType]
        else:
            self._db.create_table(  # type: ignore[reportUnknownMemberType]
                self._table_name, data=records, mode="overwrite"
            )
        logger.info("vector_upsert", count=len(chunks))

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[Chunk]:
        if not self._has_table():
            return []

        table = self._db.open_table(self._table_name)
        query = table.search(query_vector).limit(top_k)  # type: ignore[reportUnknownMemberType]

        if source_filter:
            query = query.where(f"source = '{source_filter}'")  # type: ignore[reportUnknownMemberType]

        results = cast(list[dict[str, Any]], query.to_list())  # type: ignore[reportUnknownMemberType]
        logger.info("vector_search", top_k=top_k, source_filter=source_filter, results=len(results))

        return [_row_to_chunk(row) for row in results]
