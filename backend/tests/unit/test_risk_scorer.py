"""Unit tests for keyword-based risk scanning and severity scoring."""

from __future__ import annotations

import pytest

from app.core.risk_scorer import quick_keyword_scan, severity_from_score


class TestQuickKeywordScan:
    """Tests for :func:`quick_keyword_scan`."""

    def test_critical_keyword_detected(self) -> None:
        """'unlimited liability' in text should appear under CRITICAL findings."""
        text = "The contractor accepts unlimited liability for all damages."
        findings = quick_keyword_scan(text)
        assert "CRITICAL" in findings
        assert "unlimited liability" in findings["CRITICAL"]

    def test_high_keyword_detected(self) -> None:
        """'non-compete' in text should appear under HIGH findings."""
        text = "Employee agrees to a non-compete clause for 12 months."
        findings = quick_keyword_scan(text)
        assert "HIGH" in findings
        assert "non-compete" in findings["HIGH"]

    def test_medium_keyword_detected(self) -> None:
        """'arbitration' in text should appear under MEDIUM findings."""
        text = "All disputes shall be resolved through binding arbitration."
        findings = quick_keyword_scan(text)
        assert "MEDIUM" in findings
        assert "arbitration" in findings["MEDIUM"]

    def test_no_keywords_returns_empty(self) -> None:
        """Clean text with no risk keywords should return an empty dict."""
        text = "The parties agree to meet next Tuesday for coffee."
        findings = quick_keyword_scan(text)
        assert findings == {}

    def test_multiple_severities_detected(self) -> None:
        """Text containing keywords from multiple severity levels returns all."""
        text = "Unlimited liability applies and arbitration is required."
        findings = quick_keyword_scan(text)
        assert "CRITICAL" in findings
        assert "MEDIUM" in findings

    def test_case_insensitive_matching(self) -> None:
        """Uppercase 'UNLIMITED LIABILITY' should still be detected as CRITICAL."""
        text = "UNLIMITED LIABILITY shall apply to all breaches."
        findings = quick_keyword_scan(text)
        assert "CRITICAL" in findings
        assert "unlimited liability" in findings["CRITICAL"]


class TestSeverityFromScore:
    """Tests for :func:`severity_from_score`."""

    def test_severity_from_score_critical(self) -> None:
        """Score of 9.0 should map to CRITICAL."""
        assert severity_from_score(9.0) == "CRITICAL"

    def test_severity_from_score_high(self) -> None:
        """Score of 7.5 should map to HIGH."""
        assert severity_from_score(7.5) == "HIGH"

    def test_severity_from_score_medium(self) -> None:
        """Score of 5.0 should map to MEDIUM."""
        assert severity_from_score(5.0) == "MEDIUM"

    def test_severity_from_score_low(self) -> None:
        """Score of 2.0 should map to LOW."""
        assert severity_from_score(2.0) == "LOW"

    def test_severity_from_score_info(self) -> None:
        """Score of 1.0 should map to INFO."""
        assert severity_from_score(1.0) == "INFO"

    def test_severity_boundary_critical(self) -> None:
        """Score exactly 8.0 should be CRITICAL (boundary inclusive)."""
        assert severity_from_score(8.0) == "CRITICAL"

    def test_severity_boundary_high(self) -> None:
        """Score exactly 6.0 should be HIGH (boundary inclusive)."""
        assert severity_from_score(6.0) == "HIGH"
