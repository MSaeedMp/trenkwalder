import tempfile
from pathlib import Path

import pytest

from etl.unstructured.extract import parse_markdown, parse_txt

MD_CONTENT = """# Benefits

## Health Insurance

All employees get health insurance from day one. Coverage includes medical and dental.

## Time Off

### Paid Leave

Employees receive 25 days of paid vacation per year.

### Parental Leave

New parents get 16 weeks of paid leave.
"""

TXT_CONTENT = """Code of Conduct

Our company values respect and professionalism.

Communication

Use professional language in all workplace communications.

Confidentiality

Protect company information at all times.
"""


@pytest.mark.unit
def test_parse_markdown_produces_sections() -> None:
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(MD_CONTENT)
        f.flush()
        doc = parse_markdown(Path(f.name))

    assert doc.format == "md"
    assert len(doc.pages) > 0
    texts = [p.text for p in doc.pages]
    assert any("health insurance" in t.lower() for t in texts)


@pytest.mark.unit
def test_parse_txt_splits_on_blank_lines() -> None:
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write(TXT_CONTENT)
        f.flush()
        doc = parse_txt(Path(f.name))

    assert doc.format == "txt"
    assert len(doc.pages) >= 3
