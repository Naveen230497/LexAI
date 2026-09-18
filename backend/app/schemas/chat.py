"""Pydantic schemas for the chat streaming endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation history.

    Attributes:
        role: Speaker role — either ``"user"`` or ``"assistant"``.
        content: Text content of the message.
    """

    role: str = Field(..., description="Speaker role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    """Request body for the POST /chat/{session_id}/stream endpoint.

    Attributes:
        question: The user's current question about the document.
        history: Prior conversation turns for context continuity.
    """

    question: str = Field(
        ...,
        max_length=2000,
        description="User question about the document (max 2000 chars)",
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation turns for context",
    )
