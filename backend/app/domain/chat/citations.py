import re
from dataclasses import dataclass

from app.core.observability import get_logger
from app.schemas.rag import ChunkResult

logger = get_logger(__name__)

CITATION_PATTERN = re.compile(r"\[([^\]]+?)\s+§([^\]]+?)\]")


@dataclass(frozen=True)
class Citation:
    source: str
    section: str


def parse_citations(text: str) -> list[Citation]:
    """Extract [source §section] markers from text."""
    return [
        Citation(source=m.group(1).strip(), section=m.group(2).strip())
        for m in CITATION_PATTERN.finditer(text)
    ]


def validate_citations(
    parsed: list[Citation],
    retrieved_chunks: list[ChunkResult],
) -> tuple[list[Citation], list[Citation]]:
    """Check parsed citations against retrieved chunks. Returns (valid, rejected)."""
    known = {(c.source, c.section) for c in retrieved_chunks if c.section}
    known |= {(c.source, "") for c in retrieved_chunks}

    valid: list[Citation] = []
    rejected: list[Citation] = []
    for c in parsed:
        if (c.source, c.section) in known or (c.source, "") in known:
            valid.append(c)
        else:
            logger.warning("citation_rejected", source=c.source, section=c.section)
            rejected.append(c)

    return valid, rejected
