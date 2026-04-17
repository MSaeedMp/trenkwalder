import tempfile
from pathlib import Path

import pytest

from pipelines.unstructured.extract import parse_markdown
from pipelines.unstructured.transform import chunk_document


@pytest.mark.unit
def test_markdown_chunking() -> None:
    md = "# Title\n\n## Section\n\nSome text about policies.\n\n## Other\n\nMore content here."
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(md)
        f.flush()
        doc = parse_markdown(Path(f.name))

    chunks = chunk_document(doc)
    assert len(chunks) > 0
    assert all(c.format == "md" and c.text.strip() for c in chunks)
    assert all(c.id.count(":") == 2 for c in chunks)
