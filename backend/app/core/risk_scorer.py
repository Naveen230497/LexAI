"""Keyword-based risk pre-scanning and severity scoring utilities."""

from __future__ import annotations

RISK_KEYWORDS: dict[str, list[str]] = {
    "CRITICAL": [
        "unlimited liability",
        "irrevocable",
        "in perpetuity",
        "sole discretion",
        "waive all rights",
        "indemnify and hold harmless",
    ],
    "HIGH": [
        "indemnification",
        "non-compete",
        "liquidated damages",
        "automatic renewal",
        "unilateral modification",
        "assign without consent",
    ],
    "MEDIUM": [
        "arbitration",
        "jurisdiction",
        "force majeure",
        "limitation of liability",
        "governing law",
    ],
    "LOW": [
        "severability",
        "entire agreement",
        "notice",
        "waiver",
    ],
}

RISK_COLORS: dict[str, str] = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f97316",
    "MEDIUM": "#eab308",
    "LOW": "#22c55e",
    "INFO": "#3b82f6",
}


def quick_keyword_scan(text: str) -> dict[str, list[str]]:
    """Perform a fast keyword-based pre-scan before sending text to Gemini.

    Lowercases the document text and checks for the presence of each
    keyword in ``RISK_KEYWORDS``. Used to provide immediate feedback to
    the UI and to guide prompt construction by surfacing known risk terms.

    Args:
        text: Full document text to scan.

    Returns:
        Dictionary mapping severity level strings (``"CRITICAL"``, ``"HIGH"``,
        etc.) to lists of matched keywords. Severity levels with no matches
        are omitted from the returned dictionary.
    """
    lower_text = text.lower()
    findings: dict[str, list[str]] = {}

    for severity, keywords in RISK_KEYWORDS.items():
        matched = [kw for kw in keywords if kw.lower() in lower_text]
        if matched:
            findings[severity] = matched

    return findings


def severity_from_score(score: float) -> str:
    """Convert a numeric risk score (0–10) to a severity label string.

    Thresholds:
    - ``>= 8.0`` → ``"CRITICAL"``
    - ``>= 6.0`` → ``"HIGH"``
    - ``>= 4.0`` → ``"MEDIUM"``
    - ``>= 2.0`` → ``"LOW"``
    - ``< 2.0``  → ``"INFO"``

    Args:
        score: Numeric risk score in the range [0, 10].

    Returns:
        Severity label string matching one of the ``RiskSeverity`` enum values.
    """
    if score >= 8.0:
        return "CRITICAL"
    if score >= 6.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    if score >= 2.0:
        return "LOW"
    return "INFO"
