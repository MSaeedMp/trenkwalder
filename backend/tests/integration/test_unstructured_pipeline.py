import tempfile
from pathlib import Path

import pytest

from etl.unstructured.extract import load_documents

MD_CONTENT = """# Benefits

## Health Insurance

All employees get health insurance from day one.
"""

TXT_CONTENT = """Code of Conduct

Our company values respect and professionalism.

Communication

Use professional language in all workplace communications.
"""


@pytest.mark.integration
def test_load_documents_discovers_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        md_dir = Path(tmpdir) / "md"
        md_dir.mkdir()
        (md_dir / "test.md").write_text(MD_CONTENT)

        txt_dir = Path(tmpdir) / "txt"
        txt_dir.mkdir()
        (txt_dir / "test.txt").write_text(TXT_CONTENT)

        docs = load_documents(tmpdir)
        assert len(docs) == 2
        formats = {d.format for d in docs}
        assert formats == {"md", "txt"}
