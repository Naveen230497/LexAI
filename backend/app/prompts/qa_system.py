"""Prompt template for the RAG Q&A system."""

from __future__ import annotations

QA_SYSTEM_PROMPT = """
You are a legal document assistant. Answer questions based ONLY on the provided
document context. Do not use external knowledge or make assumptions beyond the text.

IMPORTANT: You provide legal information only, not legal advice.
Always cite which section of the document your answer comes from.
If the document does not contain information to answer the question, say so clearly.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION: {question}

Provide a clear, helpful answer based solely on the document above.
"""


def build_qa_prompt(context: str, question: str, history: list[dict]) -> str:
    """Build the Q&A prompt combining retrieved context, history, and question.

    Limits conversation history to the last 6 turns to keep the prompt within
    Gemini Flash's context window while still providing meaningful continuity.

    Args:
        context: Concatenated text chunks retrieved from ChromaDB.
        question: Sanitized user question.
        history: Full conversation history as a list of
            ``{"role": str, "content": str}`` dicts.

    Returns:
        Fully formatted prompt string ready to send to Gemini.
    """
    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" for msg in history[-6:]
    )
    return QA_SYSTEM_PROMPT.format(
        context=context,
        history=history_text or "No previous conversation.",
        question=question,
    )
