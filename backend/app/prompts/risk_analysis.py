"""Prompt template for legal risk analysis."""

from __future__ import annotations

RISK_ANALYSIS_PROMPT = """
You are a legal risk analyst. Analyze the following legal document and identify
all significant risks for the party reading this document.

For each risk found, classify severity:
- CRITICAL: Deal-breakers — unlimited liability, irrevocable terms, waiving all rights
- HIGH: Significant concerns — non-compete, liquidated damages, automatic renewal
- MEDIUM: Worth reviewing — arbitration clauses, jurisdiction choices, force majeure
- LOW: Standard clauses — severability, governing law, notice requirements
- INFO: Neutral informational clauses

Respond in this EXACT JSON format:
{{
  "risks": [
    {{
      "id": "risk_1",
      "severity": "HIGH",
      "clause_text": "exact text of the risky clause",
      "section": "Section 4.2 or best guess",
      "explanation": "why this is a risk in plain English",
      "recommendation": "specific action to take or negotiate",
      "category": "LIABILITY|IP|TERMINATION|PAYMENT|CONFIDENTIALITY|OTHER"
    }}
  ],
  "overall_risk_score": 6.5,
  "summary": "2-3 sentence plain-English summary of the overall risk level"
}}

LEGAL DOCUMENT TEXT:
{text}
"""


def build_risk_analysis_prompt(text: str) -> str:
    """Build the risk analysis prompt with the provided document text.

    Truncates to 30 000 characters to stay within Gemini Flash context limits.

    Args:
        text: Extracted document text to analyze.

    Returns:
        Fully formatted prompt string ready to send to Gemini.
    """
    return RISK_ANALYSIS_PROMPT.format(text=text[:30000])
