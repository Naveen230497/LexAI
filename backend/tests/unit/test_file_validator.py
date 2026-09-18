"""Unit tests for file type and size validation."""

from __future__ import annotations

import pytest

from app.core.sanitizer import validate_file_size, validate_file_type


class TestValidateFileType:
    """Tests for :func:`validate_file_type`."""

    def test_pdf_magic_bytes_valid(self) -> None:
        """PDF magic bytes with .pdf extension should return True."""
        header = b"%PDF-1.4 rest of file content here"
        assert validate_file_type(header[:8], "contract.pdf") is True

    def test_docx_magic_bytes_valid(self) -> None:
        """DOCX magic bytes (PK ZIP header) with .docx extension should return True."""
        header = b"PK\x03\x04extra bytes here"
        assert validate_file_type(header[:8], "agreement.docx") is True

    def test_txt_file_valid(self) -> None:
        """Any bytes with .txt extension should return True (no magic check)."""
        assert validate_file_type(b"plain text content", "notes.txt") is True

    def test_exe_magic_bytes_invalid(self) -> None:
        """MZ DOS header with .exe extension should return False."""
        header = b"MZ\x90\x00\x03\x00\x00\x00"
        assert validate_file_type(header[:8], "malware.exe") is False

    def test_pdf_extension_with_wrong_magic_blocked(self) -> None:
        """MZ magic bytes declared as .pdf should return False (mismatch)."""
        header = b"MZ\x90\x00\x03\x00\x00\x00"
        assert validate_file_type(header[:8], "evil.pdf") is False

    def test_docx_extension_with_wrong_magic_blocked(self) -> None:
        """Non-ZIP magic bytes declared as .docx should return False."""
        header = b"%PDF-1.4 ooops"
        assert validate_file_type(header[:8], "fake.docx") is False

    def test_unknown_extension_invalid(self) -> None:
        """A .csv file should return False as it's not in the supported types."""
        assert validate_file_type(b"col1,col2,col3", "data.csv") is False


class TestValidateFileSize:
    """Tests for :func:`validate_file_size`."""

    def test_file_size_under_limit(self) -> None:
        """5 MB file with 10 MB limit should return True."""
        five_mb = 5 * 1024 * 1024
        assert validate_file_size(five_mb, max_mb=10) is True

    def test_file_size_at_limit(self) -> None:
        """File exactly at the limit (10 MB) should return True."""
        exactly_10mb = 10 * 1024 * 1024
        assert validate_file_size(exactly_10mb, max_mb=10) is True

    def test_file_size_over_limit(self) -> None:
        """11 MB file with 10 MB limit should return False."""
        eleven_mb = 11 * 1024 * 1024
        assert validate_file_size(eleven_mb, max_mb=10) is False

    def test_file_size_zero(self) -> None:
        """Zero-byte file should always be within any positive limit."""
        assert validate_file_size(0, max_mb=10) is True
