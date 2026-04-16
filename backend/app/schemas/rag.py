from pydantic import BaseModel, Field


class PageText(BaseModel):
    page: int
    text: str
    heading_path: list[str] = Field(default_factory=list)


class RawDocument(BaseModel):
    path: str
    format: str
    pages: list[PageText]


class DocumentMetadata(BaseModel):
    doc_id: str
    path: str
    format: str
    title: str
    num_chunks: int
    ingested_at: str


class ChunkResult(BaseModel):
    text: str
    source: str
    page: int = 0
    section: str = ""
    score: float = 0.0
