from dataclasses import dataclass

import lancedb

from app.core.config import Settings
from app.core.observability import get_logger
from app.repositories import (
    ConversationRepository,
    EmployeeRepository,
    LanceDBVectorRepository,
)
from pipelines import run_all_pipelines

logger = get_logger(__name__)


@dataclass
class Repositories:
    vector: LanceDBVectorRepository
    employee: EmployeeRepository
    conversation: ConversationRepository


def init_database(settings: Settings) -> Repositories:
    """Connect to LanceDB, run ETL pipelines, and build repositories."""
    db = lancedb.connect(settings.vector_store_path)  # type: ignore[no-untyped-call]
    run_all_pipelines(settings, db)

    return Repositories(
        vector=LanceDBVectorRepository(db),
        employee=EmployeeRepository(db),
        conversation=ConversationRepository(db),
    )
