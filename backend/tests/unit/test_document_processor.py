"""Unit tests for document text extraction and chunking."""

from __future__ import annotations

import pytest

from app.core.document_processor import (
    DocumentProcessingError,
    chunk_document,
    extract_text_from_txt,
    process_upload,
)


class TestChunkDocument:
    """Tests for :func:`chunk_document`."""

    def test_chunk_document_basic(self) -> None:
        """A 3000-character string should be split into multiple chunks.

        With the default chunk_size=1500 and overlap=200, a 3000-char string
        produces at least 2 chunks.
        """
        text = "a" * 3000
        chunks = chunk_document(text)
        assert len(chunks) > 1, "Expected multiple chunks for 3000-char text"

    def test_chunk_document_overlap(self) -> None:
        """Adjacent chunks should share at least ``overlap`` characters.

        We verify that the tail of chunk[0] appears at the head of chunk[1].
        """
        text = "x" * 3000
        chunks = chunk_document(text, chunk_size=1500, overlap=200)
        assert len(chunks) >= 2
        # The last 200 chars of chunk[0] should equal the first 200 chars of chunk[1]
        assert chunks[0][-200:] == chunks[1][:200]

    def test_chunk_document_short_text(self) -> None:
        """Text shorter than chunk_size should be returned as a single chunk."""
        text = "Short document text."
        chunks = chunk_document(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_document_exact_size(self) -> None:
        """Text exactly equal to chunk_size should return a single chunk."""
        text = "b" * 1500
        chunks = chunk_document(text, chunk_size=1500, overlap=200)
        assert len(chunks) == 1


class TestProcessUpload:
    """Tests for :func:`process_upload`."""

    def test_process_upload_unsupported_type(self) -> None:
        """Uploading a ``.exe`` file should raise ``DocumentProcessingError``."""
        with pytest.raises(DocumentProcessingError, match="Unsupported file type"):
            process_upload(b"MZ\x90\x00malware", "malware.exe")

    def test_process_upload_txt_file(self) -> None:
        """A plain ``.txt`` file should be decoded and returned as a string."""
        content = "Hello, this is a legal document."
        result = process_upload(content.encode("utf-8"), "contract.txt")
        assert result == content


class TestExtractTextFromTxt:
    """Tests for :func:`extract_text_from_txt`."""

    def test_extract_text_from_txt_utf8(self) -> None:
        """UTF-8 encoded bytes should be decoded correctly."""
        text = "Café au lait is a French phrase."
        result = extract_text_from_txt(text.encode("utf-8"))
        assert result == text

    def test_extract_text_from_txt_fallback(self) -> None:
        """Non-UTF-8 bytes should fall back to latin-1 without raising."""
        # 0x96 is an em-dash in Windows-1252 / latin-1, not valid UTF-8
        raw = b"Agreement\x96signed."
        result = extract_text_from_txt(raw)
        assert "Agreement" in result
        assert "signed" in result
