import tempfile
from pathlib import Path

import pytest

from pipelines.structured.extract import read_csv
from pipelines.structured.transform import to_employees

CSV_CONTENT = """id,name,email,department,role,manager,start_date,location
e001,Alice,alice@test.com,Engineering,Developer,Bob,2021-01-01,Vienna
e002,Bob,bob@test.com,Engineering,Manager,,2019-06-01,Vienna
e003,Charlie,charlie@test.com,Sales,Rep,Diana,2022-03-15,Graz
"""


@pytest.mark.unit
def test_extract_reads_csv() -> None:
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write(CSV_CONTENT)
        f.flush()
        df = read_csv(Path(f.name))
    assert len(df) == 3
    assert "department" in df.columns


@pytest.mark.unit
def test_transform_produces_employees() -> None:
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write(CSV_CONTENT)
        f.flush()
        df = read_csv(Path(f.name))

    employees = to_employees(df)
    assert len(employees) == 3
    assert employees[0].name == "Alice"
    assert employees[1].department == "Engineering"
    assert employees[2].location == "Graz"


@pytest.mark.unit
def test_transform_rejects_missing_columns() -> None:
    import polars as pl

    df = pl.DataFrame({"id": ["1"], "name": ["Alice"]})
    with pytest.raises(ValueError, match="CSV missing columns"):
        to_employees(df)
