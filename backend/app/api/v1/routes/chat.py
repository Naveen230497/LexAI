"""Streaming chat route handler — SSE token stream via RAG."""

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.v1.routes.documents import SESSION_STORE
from app.config import get_settings
from app.core.document_processor import chunk_document
from app.core.gemini_client import GeminiClient, get_gemini_client
from app.core.rag_engine import RAGEngine
from app.core.sanitizer import sanitize_query
from app.limiter import limiter
from app.schemas.chat import ChatRequest

router = APIRouter()


@router.post("/{session_id}/stream")
@limiter.limit("10/minute")
async def stream_chat(
    session_id: str,
    chat_request: ChatRequest,
    request: Request,
) -> StreamingResponse:
    """Stream a RAG-grounded answer to a question about the uploaded document.

    Validates the session, sanitizes the question against prompt injection,
    indexes the document into ChromaDB (per request; cheap because ChromaDB
    reuses an existing collection on disk), and streams Gemini's answer as SSE.

    Args:
        session_id: UUID of the document session to query.
        chat_request: Validated request body with question and conversation history.
        request: FastAPI request object (required by slowapi rate limiter).

    Returns:
        ``StreamingResponse`` with ``text/event-stream`` content type carrying
        ``data: {"token": "..."}`` lines terminated by ``data: [DONE]``.

    Raises:
        HTTPException 400: If the question contains a prompt injection pattern.
        HTTPException 404: If the session ID does not exist.
    """
    session = SESSION_STORE.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Please upload a document first.",
        )

    try:
        clean_question = sanitize_query(chat_request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings = get_settings()
    gemini_client: GeminiClient = get_gemini_client()

    rag_engine = RAGEngine(
        session_id=session_id,
        chroma_dir=settings.CHROMA_DIR,
        gemini_client=gemini_client,
        embedding_model=settings.GEMINI_EMBEDDING_MODEL,
    )

    text: str = session["text"]
    chunks = chunk_document(text)
    rag_engine.index_document(chunks)

    history = [msg.model_dump() for msg in chat_request.history]

    async def generate():
        """Yield SSE-formatted token events then a DONE sentinel.

        Yields:
            Server-sent event strings in the form ``data: {...}\\n\\n``.
        """
        async for token in rag_engine.stream_answer(clean_question, history):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            # Security: no-cache prevents proxies from buffering the SSE stream,
            # which would break real-time token delivery to the client.
            "Cache-Control": "no-cache",
            # X-Accel-Buffering: no disables Nginx proxy buffering so tokens
            # are forwarded immediately rather than batched.
            "X-Accel-Buffering": "no",
        },
    )
