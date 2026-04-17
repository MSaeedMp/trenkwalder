from pydantic import BaseModel, Field


class PageText(BaseModel):
    page: int
    text: str
    heading_path: list[str] = Field(default_factory=list)


class RawDocument(BaseModel):
    path: str
    format: str
    pages: list[PageText]


class ChunkResult(BaseModel):
    text: str
    source: str
    page: int = 0
    section: str = ""
    score: float = 0.0
