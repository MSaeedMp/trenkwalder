from dataclasses import asdict

import lancedb

from app.models import Chunk


def write_chunks(db: lancedb.DBConnection, chunks: list[Chunk]) -> None:
    """Write embedded chunks to the LanceDB chunks table."""
    if not chunks:
        return
    records = [asdict(c) for c in chunks]
    db.create_table("chunks", data=records, mode="overwrite")  # type: ignore[reportUnknownMemberType]
