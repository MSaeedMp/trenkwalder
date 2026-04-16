from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    text: str
    vector: list[float] = field(default_factory=lambda: list[float]())
    source: str = ""
    format: str = ""
    page: int = 0
    section: str = ""
    heading_path: list[str] = field(default_factory=lambda: list[str]())
    char_start: int = 0
    char_end: int = 0
