"""Shared pytest fixtures for LexAI backend tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.gemini_client import GeminiClient
from app.main import app

SAMPLE_SIMPLIFICATION: dict = {
    "document_type": "Non-Disclosure Agreement",
    "plain_english": "This is a confidentiality agreement.",
    "key_points": ["Keep information secret", "2 year duration"],
    "unusual_clauses": [],
}

SAMPLE_RISK_ANALYSIS: dict = {
    "risks": [
        {
            "id": "risk_1",
            "severity": "HIGH",
            "clause_text": "unlimited liability",
            "section": "Section 5",
            "explanation": "No cap on damages",
            "recommendation": "Negotiate a liability cap",
            "category": "LIABILITY",
        }
    ],
    "overall_risk_score": 6.5,
    "summary": "Moderate risk document.",
}


async def _aiter(items: list[str]):
    """Async generator helper that yields items one by one.

    Args:
        items: List of string tokens to yield.

    Yields:
        Each item in order.
    """
    for item in items:
        yield item


@pytest.fixture
def mock_gemini_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock GeminiClient to prevent real API calls during tests.

    All tests using this fixture run without Gemini quota consumption.
    The ``generate_json`` side_effect list is ordered so the first call
    returns the simplification result and the second returns the risk analysis.

    Args:
        monkeypatch: pytest monkeypatch fixture for attribute patching.

    Returns:
        Configured ``MagicMock`` matching the ``GeminiClient`` spec.
    """
    mock = MagicMock(spec=GeminiClient)
    mock.generate_json = AsyncMock(
        side_effect=[
            SAMPLE_SIMPLIFICATION,
            SAMPLE_RISK_ANALYSIS,
        ]
    )
    mock.stream_generate = MagicMock(return_value=_aiter(["This ", "is ", "a ", "test."]))
    mock.embed_texts = MagicMock(return_value=[[0.1] * 768])

    monkeypatch.setattr(
        "app.api.v1.routes.analysis.get_gemini_client", lambda: mock
    )
    monkeypatch.setattr(
        "app.api.v1.routes.chat.get_gemini_client", lambda: mock
    )
    return mock


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP test client for the FastAPI app.

    Yields:
        Configured ``AsyncClient`` targeting the in-process ASGI app.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid PDF magic bytes for upload tests.

    Returns:
        Bytes starting with the PDF magic header ``%PDF``.
    """
    return b"%PDF-1.4 sample content for testing purposes only"


@pytest.fixture
def sample_nda_text() -> str:
    """Sample NDA text loaded from the fixture file.

    Returns:
        Full NDA text as a string.
    """
    fixture_path = Path(__file__).parent / "fixtures" / "sample_nda.txt"
    return fixture_path.read_text(encoding="utf-8")
