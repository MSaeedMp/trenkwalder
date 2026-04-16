from pathlib import Path

import lancedb

from app.core.observability import get_logger
from pipelines.structured.extract import read_csv
from pipelines.structured.load import write_employees
from pipelines.structured.transform import to_employees

logger = get_logger(__name__)


def run_structured(docs_dir: str, db: lancedb.DBConnection) -> None:
    """Run the structured ETL pipeline: CSV → Employee dataclass → LanceDB."""
    csv_path = Path(docs_dir) / "csv" / "employees.csv"
    if not csv_path.exists():
        logger.warning("structured_skipped", reason="CSV not found", path=str(csv_path))
        return

    logger.info("structured_started", source=str(csv_path))

    df = read_csv(csv_path)
    employees = to_employees(df)
    write_employees(db, employees)

    logger.info("structured_completed", rows_loaded=len(employees))
