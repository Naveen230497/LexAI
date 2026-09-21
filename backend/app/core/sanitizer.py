from functools import lru_cache
"""Input sanitization utilities for prompt injection prevention."""

from __future__ import annotations

import re


# Security: These patterns match the most common prompt injection techniques where
# a malicious actor embeds instructions inside an uploaded document to override
# the system prompt. Blocking them prevents the model from being hijacked.
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore.*instructions", re.IGNORECASE),
    re.compile(r"you are now", re.IGNORECASE),
    re.compile(r"act as", re.IGNORECASE),
    re.compile(r"disregard.*previous", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
    re.compile(r"<\|.*?\|>", re.IGNORECASE | re.DOTALL),
]

# Security: These magic byte sequences identify the true file format regardless
# of the file extension. Extension-only validation is trivially bypassed by
# renaming a malicious file (e.g., malware.exe -> document.pdf).
_MAGIC_BYTES: dict[str, bytes] = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
}

_MAX_QUERY_LENGTH: int = 2000


@lru_cache(maxsize=500)
def sanitize_query(query: str) -> str:
    """Sanitize a user query to prevent prompt injection attacks.

    Strips leading/trailing whitespace and truncates to ``_MAX_QUERY_LENGTH``
    characters. Raises ``ValueError`` if the query contains patterns commonly
    used to override LLM system instructions.

    Args:
        query: Raw user-supplied query string.

    Returns:
        Sanitized query string, stripped and truncated as necessary.

    Raises:
        ValueError: If the query contains a detected prompt injection pattern.
    """
    query = query.strip()
    query = query[:_MAX_QUERY_LENGTH]

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(query):
            raise ValueError(
                f"Query contains a disallowed pattern: '{pattern.pattern}'. "
                "Possible prompt injection attempt."
            )

    return query


def validate_file_type(header_bytes: bytes, filename: str) -> bool:
    """Validate an upload by inspecting magic bytes rather than file extension.

    Extension-only validation is bypassed by renaming files. Magic bytes
    inspection reads the actual binary format header to confirm the file is
    what it claims to be.

    Supported types:
    - PDF: magic ``b'%PDF'``
    - DOCX: magic ``b'PK\\x03\\x04'`` (ZIP-based Office Open XML)
    - TXT: no magic bytes required; any extension ``.txt`` is accepted.

    Args:
        header_bytes: First ``N`` bytes of the uploaded file (at least 8 bytes).
        filename: Original filename, used only to check the declared extension.

    Returns:
        ``True`` if the file passes validation, ``False`` otherwise.
    """
    lower_name = filename.lower()

    if lower_name.endswith(".txt"):
        # Security: Plain text files have no magic bytes, but we still require
        # the declared extension to be .txt to limit accepted content types.
        return True

    for extension, magic in _MAGIC_BYTES.items():
        if lower_name.endswith(extension):
            # Security: Verify the binary header matches the declared type.
            # A renamed executable will have MZ/ELF magic bytes, not PDF/ZIP.
            return header_bytes[:len(magic)] == magic

    return False


def validate_file_size(size_bytes: int, max_mb: int) -> bool:
    """Check whether a file's size is within the configured maximum.

    Args:
        size_bytes: Size of the file in bytes.
        max_mb: Maximum allowed file size in megabytes.

    Returns:
        ``True`` if the file is within the limit, ``False`` if it exceeds it.
    """
    return size_bytes <= max_mb * 1024 * 1024

