"""Integration tests for the full analysis endpoint."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.core.gemini_client import GeminiClient
from app.schemas.analysis import RiskSeverity

SAMPLE_SIMPLIFICATION = {
    "document_type": "Non-Disclosure Agreement",
    "plain_english": "This is a confidentiality agreement.",
    "key_points": ["Keep information secret", "2 year duration"],
    "unusual_clauses": [],
}

SAMPLE_RISK_ANALYSIS = {
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


async def _upload_txt_document(client: AsyncClient, content: bytes = b"Test legal text.") -> str:
    """Helper: upload a TXT document and return the session_id.

    Args:
        client: Async test client.
        content: File bytes to upload.

    Returns:
        Session ID string from the upload response.
    """
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    return response.json()["session_id"]


class TestFullAnalysisEndpoint:
    """Integration tests for POST /api/v1/analysis/{session_id}/full."""

    async def test_full_analysis_returns_expected_shape(
        self,
        client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Full analysis response should contain both simplification and risk_analysis keys."""
        mock = MagicMock(spec=GeminiClient)
        mock.generate_json = AsyncMock(
            side_effect=[SAMPLE_SIMPLIFICATION, SAMPLE_RISK_ANALYSIS]
        )
        monkeypatch.setattr(
            "app.api.v1.routes.analysis.get_gemini_client", lambda: mock
        )

        session_id = await _upload_txt_document(client)

        response = await client.post(f"/api/v1/analysis/{session_id}/full")
        assert response.status_code == 200

        data = response.json()
        assert "simplification" in data
        assert "risk_analysis" in data
        assert "plain_english" in data["simplification"]
        assert "risks" in data["risk_analysis"]

    async def test_analysis_invalid_session_404(self, client: AsyncClient) -> None:
        """Analysis on a non-existent session_id should return HTTP 404."""
        response = await client.post(
            "/api/v1/analysis/00000000-0000-0000-0000-000000000000/full"
        )
        assert response.status_code == 404

    async def test_risk_analysis_has_severity_enum(
        self,
        client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Every risk entry in the response should have a valid RiskSeverity value."""
        mock = MagicMock(spec=GeminiClient)
        mock.generate_json = AsyncMock(
            side_effect=[SAMPLE_SIMPLIFICATION, SAMPLE_RISK_ANALYSIS]
        )
        monkeypatch.setattr(
            "app.api.v1.routes.analysis.get_gemini_client", lambda: mock
        )

        session_id = await _upload_txt_document(client)
        response = await client.post(f"/api/v1/analysis/{session_id}/full")
        assert response.status_code == 200

        risks = response.json()["risk_analysis"]["risks"]
        valid_severities = {s.value for s in RiskSeverity}
        for risk in risks:
            assert risk["severity"] in valid_severities, (
                f"Invalid severity value: {risk['severity']}"
            )

    async def test_analysis_response_is_cached(
        self,
        client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Calling full analysis twice with the same document should only call Gemini once."""
        from app.core.cache import response_cache

        response_cache.clear()

        mock = MagicMock(spec=GeminiClient)
        mock.generate_json = AsyncMock(
            side_effect=[
                SAMPLE_SIMPLIFICATION,
                SAMPLE_RISK_ANALYSIS,
                # If called a third or fourth time the test will fail with StopAsyncIteration
            ]
        )
        monkeypatch.setattr(
            "app.api.v1.routes.analysis.get_gemini_client", lambda: mock
        )

        content = b"Unique caching test document content."
        session_id = await _upload_txt_document(client, content=content)

        response1 = await client.post(f"/api/v1/analysis/{session_id}/full")
        assert response1.status_code == 200

        response2 = await client.post(f"/api/v1/analysis/{session_id}/full")
        assert response2.status_code == 200

        # generate_json should have been called exactly twice (once per analysis type)
        # on the first request only — the second hit the cache.
        assert mock.generate_json.call_count == 2
