from pathlib import Path

from markdown_it import MarkdownIt
from pypdf import PdfReader

from app.schemas.rag import PageText, RawDocument


def discover_files(docs_dir: str) -> list[Path]:
    """Find all PDF, MD, and TXT files in the docs directory."""
    base = Path(docs_dir)
    files: list[Path] = []
    for subdir, extensions in [("pdf", "*.pdf"), ("md", "*.md"), ("txt", "*.txt")]:
        files.extend(sorted((base / subdir).glob(extensions)))
    return files


def parse_pdf(path: Path) -> RawDocument:
    """Extract text from each page of a PDF."""
    reader = PdfReader(path)
    pages = [
        PageText(page=i + 1, text=page.extract_text() or "") for i, page in enumerate(reader.pages)
    ]
    return RawDocument(path=str(path), format="pdf", pages=pages)


def parse_markdown(path: Path) -> RawDocument:
    """Parse Markdown into heading-aware page segments."""
    text = path.read_text(encoding="utf-8")
    md = MarkdownIt()
    tokens = md.parse(text)

    pages: list[PageText] = []
    # Keep the current heading trail so retrieved chunks can cite a useful section.
    heading_path: list[str] = []
    current_text: list[str] = []
    section_idx = 0

    for token in tokens:
        if token.type == "heading_open":
            if current_text:
                joined = "\n".join(current_text).strip()
                if joined:
                    pages.append(
                        PageText(
                            page=section_idx,
                            text=joined,
                            heading_path=list(heading_path),
                        )
                    )
                    section_idx += 1
                current_text = []

            level = int(token.tag[1]) if token.tag.startswith("h") else 1
            heading_path = heading_path[: level - 1]

        elif token.type == "inline" and token.content:
            if tokens[tokens.index(token) - 1].type == "heading_open":
                heading_path.append(token.content)
            current_text.append(token.content)

    if current_text:
        joined = "\n".join(current_text).strip()
        if joined:
            pages.append(
                PageText(
                    page=section_idx,
                    text=joined,
                    heading_path=list(heading_path),
                )
            )

    return RawDocument(path=str(path), format="md", pages=pages)


def parse_txt(path: Path) -> RawDocument:
    """Parse a plain text file, splitting on blank lines into paragraphs."""
    text = path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pages = [PageText(page=i, text=para) for i, para in enumerate(paragraphs)]
    return RawDocument(path=str(path), format="txt", pages=pages)


LOADERS = {
    ".pdf": parse_pdf,
    ".md": parse_markdown,
    ".txt": parse_txt,
}


def load_documents(docs_dir: str) -> list[RawDocument]:
    """Discover and parse all supported document files."""
    docs: list[RawDocument] = []
    for file_path in discover_files(docs_dir):
        loader = LOADERS.get(file_path.suffix.lower())
        if loader:
            docs.append(loader(file_path))
    return docs
