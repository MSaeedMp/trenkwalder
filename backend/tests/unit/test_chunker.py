import tempfile
from pathlib import Path

import pytest

from etl.unstructured.extract import parse_markdown
from etl.unstructured.transform import chunk_document

MD_CONTENT = """# Benefits

## Health Insurance

All employees get health insurance from day one. Coverage includes medical and dental.

## Time Off

### Paid Leave

Employees receive 25 days of paid vacation per year.

### Parental Leave

New parents get 16 weeks of paid leave.
"""


@pytest.mark.unit
def test_chunk_document_produces_chunks() -> None:
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(MD_CONTENT)
        f.flush()
        doc = parse_markdown(Path(f.name))

    chunks = chunk_document(doc)
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.source != ""
        assert chunk.format == "md"
        assert chunk.text.strip() != ""


@pytest.mark.unit
def test_chunk_ids_are_well_formed() -> None:
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(MD_CONTENT)
        f.flush()
        doc = parse_markdown(Path(f.name))

    chunks = chunk_document(doc)
    for chunk in chunks:
        parts = chunk.id.split(":")
        assert len(parts) == 3
        assert parts[0].endswith(".md")
