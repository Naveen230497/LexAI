"""Document text extraction and chunking utilities."""

from __future__ import annotations

import io


class DocumentProcessingError(Exception):
    """Raised when a document cannot be extracted or processed.

    This is a domain-level exception that route handlers catch and convert
    to appropriate HTTP error responses.
    """


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF.

    Args:
        file_bytes: Raw PDF file bytes.

    Returns:
        Concatenated text content from all pages.

    Raises:
        DocumentProcessingError: If the PDF is encrypted, corrupted, or
            yields no extractable text.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise DocumentProcessingError("PyMuPDF is not installed.") from exc

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise DocumentProcessingError(f"Could not open PDF: {exc}") from exc

    if doc.is_encrypted:
        raise DocumentProcessingError(
            "The uploaded PDF is encrypted. Please provide an unlocked document."
        )

    pages: list[str] = []
    for page in doc:
        pages.append(page.get_text())

    doc.close()

    text = "\n".join(pages).strip()
    if not text:
        raise DocumentProcessingError(
            "No extractable text found in the PDF. "
            "The file may be a scanned image without OCR."
        )

    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx.

    Preserves paragraph structure by joining paragraphs with double newlines,
    which helps downstream chunking respect natural document boundaries.

    Args:
        file_bytes: Raw DOCX file bytes.

    Returns:
        Extracted text with paragraphs separated by double newlines.

    Raises:
        DocumentProcessingError: If the DOCX file cannot be opened or parsed.
    """
    try:
        from docx import Document
    except ImportError as exc:
        raise DocumentProcessingError("python-docx is not installed.") from exc

    try:
        document = Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise DocumentProcessingError(f"Could not open DOCX file: {exc}") from exc

    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode plain text bytes with UTF-8, falling back to latin-1.

    Latin-1 is chosen as the fallback because it can decode any byte sequence
    (every byte maps to a valid code point), avoiding ``UnicodeDecodeError``
    on files with legacy Windows-1252 or ISO-8859-1 encoding.

    Args:
        file_bytes: Raw text file bytes.

    Returns:
        Decoded string content.
    """
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def process_upload(file_bytes: bytes, filename: str) -> str:
    """Route file bytes to the correct extractor based on file extension.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original filename, used to determine the file type.

    Returns:
        Extracted plain-text content of the document.

    Raises:
        DocumentProcessingError: If the file extension is not supported.
    """
    lower = filename.lower()

    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    if lower.endswith(".txt"):
        return extract_text_from_txt(file_bytes)

    raise DocumentProcessingError(
        f"Unsupported file type for '{filename}'. "
        "Accepted types: .pdf, .docx, .txt"
    )


def chunk_document(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 200,
) -> list[str]:
    """Split document text into overlapping chunks for vector embedding.

    Overlap of 200 characters ensures that legal clause meaning is not
    truncated at arbitrary chunk boundaries — a clause that straddles a
    boundary will appear fully in at least one of the two adjacent chunks.

    Chunk size of 1500 balances retrieval precision against context
    preservation: too small and multi-sentence clauses lose context;
    too large and retrieval returns irrelevant surrounding text.

    Args:
        text: Full document text to chunk.
        chunk_size: Maximum characters per chunk.
        overlap: Number of characters shared between adjacent chunks.

    Returns:
        List of text chunks. Returns a single-element list if the text
        is shorter than ``chunk_size``.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap

    return chunks
