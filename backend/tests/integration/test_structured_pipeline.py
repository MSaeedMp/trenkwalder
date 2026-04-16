import tempfile
from pathlib import Path

import lancedb
import pytest

from etl.structured.extract import read_csv
from etl.structured.load import write_employees
from etl.structured.pipeline import run_structured
from etl.structured.transform import to_employees

CSV_CONTENT = """id,name,email,department,role,manager,start_date,location
e001,Alice,alice@test.com,Engineering,Developer,Bob,2021-01-01,Vienna
e002,Bob,bob@test.com,Engineering,Manager,,2019-06-01,Vienna
e003,Charlie,charlie@test.com,Sales,Rep,Diana,2022-03-15,Graz
"""


@pytest.mark.integration
def test_load_writes_to_lancedb() -> None:
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write(CSV_CONTENT)
        f.flush()
        df = read_csv(Path(f.name))

    employees = to_employees(df)

    with tempfile.TemporaryDirectory() as tmpdir:
        db = lancedb.connect(tmpdir)
        write_employees(db, employees)

        assert "employees" in db.list_tables().tables
        table = db.open_table("employees")
        assert table.count_rows() == 3


@pytest.mark.integration
def test_structured_pipeline_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_dir = Path(tmpdir) / "docs" / "csv"
        csv_dir.mkdir(parents=True)
        (csv_dir / "employees.csv").write_text(CSV_CONTENT)

        db = lancedb.connect(str(Path(tmpdir) / "lancedb"))
        run_structured(str(csv_dir.parent), db)

        assert "employees" in db.list_tables().tables
        assert db.open_table("employees").count_rows() == 3
