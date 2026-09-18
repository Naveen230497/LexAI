"""Prompt template for legal document simplification."""

from __future__ import annotations

SIMPLIFICATION_PROMPT = """
You are a legal document simplifier. Convert the following legal document text
to plain English that any adult without legal training can understand.

RULES:
1. Replace legal jargon with everyday language — keep exact meaning
2. Use bullet points for lists of conditions or obligations
3. Flag unusual or potentially unfavorable clauses with ⚠️
4. Identify the document type (e.g. NDA, Employment Contract, Terms of Service)
5. Do NOT omit any meaningful content

Respond in this EXACT JSON format:
{{
  "document_type": "...",
  "plain_english": "...",
  "key_points": ["point 1", "point 2", ...],
  "unusual_clauses": ["clause description 1", ...]
}}

LEGAL DOCUMENT TEXT:
{text}
"""


def build_simplification_prompt(text: str) -> str:
    """Build the document simplification prompt with the provided text.

    Truncates to 30 000 characters to stay within Gemini Flash context limits.

    Args:
        text: Extracted document text to simplify.

    Returns:
        Fully formatted prompt string ready to send to Gemini.
    """
    # Truncate to 30000 chars to stay within Flash context limits
    return SIMPLIFICATION_PROMPT.format(text=text[:30000])
