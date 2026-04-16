from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra context (validation details, entity IDs, etc.)",
    )
