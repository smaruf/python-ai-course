import io
from typing import Union


def extract_text(contents: Union[bytes, str], filename: str) -> str:
    """Extract plain text from a PDF or text file.

    Supports .pdf (via pypdf) and plain text files.
    """
    if filename.lower().endswith(".pdf"):
        return _extract_pdf(contents)
    # Fallback: treat as plain text
    if isinstance(contents, bytes):
        return contents.decode("utf-8", errors="replace")
    return contents


def _extract_pdf(contents: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(contents))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF: {exc}") from exc
