"""Document upload and retrieval route handlers."""

import uuid

from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.config import get_settings
from app.core.document_processor import DocumentProcessingError, process_upload
from app.core.sanitizer import validate_file_size, validate_file_type
from app.limiter import limiter
from app.schemas.document import DocumentInfo, DocumentUploadResponse

router = APIRouter()

# Module-level session store mapping session_id â†’ document metadata and content.
# In production this would be replaced by Redis or a database, but for the scope
# of this application an in-process dict is sufficient and avoids external deps.
SESSION_STORE: dict[str, dict] = {}


@router.post("/upload", response_model=DocumentUploadResponse)
@limiter.limit("20/minute")
async def upload_document(request: Request, file: UploadFile) -> DocumentUploadResponse:
    """Upload a legal document and prepare it for analysis.

    Validates the file type via magic bytes and enforces the configured size
    limit, then extracts text and stores the session for later analysis and chat.

    Args:
        request: FastAPI request object (required by slowapi rate limiter).
        file: Multipart uploaded file (PDF, DOCX, or TXT).

    Returns:
        ``DocumentUploadResponse`` containing the new session ID.

    Raises:
        HTTPException 400: If the file type is unsupported or magic bytes mismatch.
        HTTPException 413: If the file exceeds the configured size limit.
        HTTPException 500: If text extraction fails unexpectedly.
    """
    settings = get_settings()
    file_bytes = await file.read()
    filename = file.filename or "upload"

    # Security: Validate file size before processing to prevent resource
    # exhaustion from oversized payloads before attempting text extraction.
    if not validate_file_size(len(file_bytes), settings.MAX_FILE_SIZE_MB):
        raise HTTPException(
            status_code=413,
            detail=(
                f"File size {len(file_bytes) / 1024 / 1024:.1f} MB exceeds "
                f"the {settings.MAX_FILE_SIZE_MB} MB limit."
            ),
        )

    # Security: Inspect magic bytes rather than trusting the file extension so
    # a renamed executable (e.g., malware.exe â†’ document.pdf) is rejected.
    if not validate_file_type(file_bytes[:8], filename):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported or mismatched file type for '{filename}'. "
                "Accepted types: .pdf, .docx, .txt"
            ),
        )

    try:
        text = process_upload(file_bytes, filename)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session_id = str(uuid.uuid4())
    SESSION_STORE[session_id] = {
        "filename": filename,
        "size_bytes": len(file_bytes),
        "text": text,
        "file_bytes": file_bytes,
        "status": "ready",
    }

    return DocumentUploadResponse(
        session_id=session_id,
        filename=filename,
        size_bytes=len(file_bytes),
        status="ready",
    )


@router.get("/{session_id}", response_model=DocumentInfo)
async def get_document_info(session_id: str) -> DocumentInfo:
    """Retrieve metadata for a previously uploaded document session.

    Args:
        session_id: UUID of the document session returned by the upload endpoint.

    Returns:
        ``DocumentInfo`` with filename, size, and current status.

    Raises:
        HTTPException 404: If the session ID does not exist in the store.
    """
    session = SESSION_STORE.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Please upload a document first.",
        )

    return DocumentInfo(
        session_id=session_id,
        filename=session["filename"],
        size_bytes=session["size_bytes"],
        status=session["status"],
    )

