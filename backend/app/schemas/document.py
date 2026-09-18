"""Pydantic schemas for document upload and retrieval endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response returned after a successful document upload.

    Attributes:
        session_id: Unique identifier for this document session.
        filename: Original filename of the uploaded document.
        size_bytes: Size of the uploaded file in bytes.
        status: Always ``"ready"`` on successful upload.
    """

    session_id: str = Field(..., description="Unique session identifier (UUID4)")
    filename: str = Field(..., description="Original filename of the uploaded document")
    size_bytes: int = Field(..., description="Size of the uploaded file in bytes")
    status: str = Field(default="ready", description="Upload status")


class DocumentInfo(BaseModel):
    """Document metadata returned by the GET /documents/{session_id} endpoint.

    Attributes:
        session_id: Unique identifier for this document session.
        filename: Original filename of the uploaded document.
        size_bytes: Size of the uploaded file in bytes.
        status: Current session status string.
    """

    session_id: str = Field(..., description="Unique session identifier")
    filename: str = Field(..., description="Original filename of the document")
    size_bytes: int = Field(..., description="Size of the document in bytes")
    status: str = Field(..., description="Current session status")
