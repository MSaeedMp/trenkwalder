import pytest

from app.domain.chat.citations import Citation, parse_citations, validate_citations
from app.schemas.rag import ChunkResult


@pytest.mark.unit
def test_parse_single_citation() -> None:
    text = "Employees get 25 days off [benefits.md §Paid Leave]."
    result = parse_citations(text)
    assert len(result) == 1
    assert result[0].source == "benefits.md"
    assert result[0].section == "Paid Leave"


@pytest.mark.unit
def test_parse_multiple_citations() -> None:
    text = "See [handbook.pdf §Expenses] and [benefits.md §Health Insurance] for details."
    result = parse_citations(text)
    assert len(result) == 2


@pytest.mark.unit
def test_parse_no_citations() -> None:
    text = "This text has no citations at all."
    assert parse_citations(text) == []


@pytest.mark.unit
def test_validate_valid_citation() -> None:
    parsed = [Citation(source="benefits.md", section="Paid Leave")]
    chunks = [ChunkResult(text="...", source="benefits.md", section="Paid Leave")]
    valid, rejected = validate_citations(parsed, chunks)
    assert len(valid) == 1
    assert len(rejected) == 0


@pytest.mark.unit
def test_validate_rejects_unknown_source() -> None:
    parsed = [Citation(source="fake.md", section="Nope")]
    chunks = [ChunkResult(text="...", source="benefits.md", section="Paid Leave")]
    valid, rejected = validate_citations(parsed, chunks)
    assert len(valid) == 0
    assert len(rejected) == 1


@pytest.mark.unit
def test_validate_accepts_source_without_section() -> None:
    parsed = [Citation(source="benefits.md", section="Some Section")]
    chunks = [ChunkResult(text="...", source="benefits.md", section="")]
    valid, _rejected = validate_citations(parsed, chunks)
    assert len(valid) == 1
