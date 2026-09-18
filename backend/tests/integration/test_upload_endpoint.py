"""Integration tests for the document upload and retrieval endpoints."""

from __future__ import annotations

import io
import uuid

import pytest
from httpx import AsyncClient


class TestUploadEndpoint:
    """Integration tests for POST /api/v1/documents/upload."""

    async def test_upload_txt_file_success(self, client: AsyncClient) -> None:
        """Uploading a valid TXT file should return HTTP 200 with a session_id."""
        content = b"This is a valid plain text legal document for testing."
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_contract.txt", io.BytesIO(content), "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["filename"] == "test_contract.txt"
        assert data["status"] == "ready"

    async def test_upload_returns_session_id_format(self, client: AsyncClient) -> None:
        """The session_id in the upload response must be a valid UUID4 string."""
        content = b"Plain text document content."
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("contract.txt", io.BytesIO(content), "text/plain")},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        # Validate it parses as a UUID without raising
        parsed = uuid.UUID(session_id)
        assert str(parsed) == session_id

    async def test_upload_too_large_rejected(self, client: AsyncClient) -> None:
        """A file exceeding MAX_FILE_SIZE_MB (10 MB) should return HTTP 413."""
        # Create an 11 MB payload
        oversized = b"x" * (11 * 1024 * 1024)
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("big.txt", io.BytesIO(oversized), "text/plain")},
        )
        assert response.status_code == 413

    async def test_upload_invalid_type_rejected(self, client: AsyncClient) -> None:
        """Uploading a .exe file should return HTTP 400."""
        exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00malicious content"
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("malware.exe", io.BytesIO(exe_bytes), "application/octet-stream")},
        )
        assert response.status_code == 400

    async def test_upload_pdf_magic_mismatch_rejected(self, client: AsyncClient) -> None:
        """A .pdf file with non-PDF magic bytes should return HTTP 400."""
        fake_pdf = b"MZ\x90\x00 this is not a pdf"
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("evil.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        assert response.status_code == 400


class TestGetDocumentInfo:
    """Integration tests for GET /api/v1/documents/{session_id}."""

    async def test_get_document_info(self, client: AsyncClient) -> None:
        """After uploading, GET /documents/{session_id} should return document metadata."""
        content = b"Legal document for retrieval test."
        upload_response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("nda.txt", io.BytesIO(content), "text/plain")},
        )
        assert upload_response.status_code == 200
        session_id = upload_response.json()["session_id"]

        get_response = await client.get(f"/api/v1/documents/{session_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["session_id"] == session_id
        assert data["filename"] == "nda.txt"
        assert data["status"] == "ready"

    async def test_get_nonexistent_session(self, client: AsyncClient) -> None:
        """GET /documents/{fake-id} for a non-existent session should return HTTP 404."""
        response = await client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
