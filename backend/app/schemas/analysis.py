"""Pydantic schemas for document analysis endpoints."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """Severity classification for identified legal risks.

    Variants:
        CRITICAL: Deal-breaking risks such as unlimited liability or irrevocable terms.
        HIGH: Significant concerns such as non-compete clauses or automatic renewal.
        MEDIUM: Clauses worth reviewing such as arbitration or force majeure.
        LOW: Standard boilerplate clauses that rarely cause issues.
        INFO: Neutral informational clauses with no inherent risk.
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class RiskEntry(BaseModel):
    """A single identified risk within the legal document.

    Attributes:
        id: Unique identifier for this risk entry (e.g. ``"risk_1"``).
        severity: Severity classification of the risk.
        clause_text: Exact text of the risky clause from the document.
        section: Document section reference (e.g. ``"Section 4.2"``).
        explanation: Plain-English explanation of why this is a risk.
        recommendation: Specific action the reader should take or negotiate.
        category: Broad risk category label.
    """

    id: str = Field(..., description="Unique risk identifier")
    severity: RiskSeverity = Field(..., description="Severity level of the risk")
    clause_text: str = Field(..., description="Exact text of the risky clause")
    section: str = Field(..., description="Document section reference")
    explanation: str = Field(..., description="Plain-English explanation of the risk")
    recommendation: str = Field(..., description="Recommended action or negotiation point")
    category: str = Field(
        ...,
        description="Risk category: LIABILITY|IP|TERMINATION|PAYMENT|CONFIDENTIALITY|OTHER",
    )


class RiskAnalysisResult(BaseModel):
    """Aggregated result of the risk analysis pass.

    Attributes:
        risks: List of individual risk entries found in the document.
        overall_risk_score: Composite risk score from 0 (no risk) to 10 (extreme risk).
        summary: 2-3 sentence plain-English summary of the overall risk level.
    """

    risks: list[RiskEntry] = Field(default_factory=list, description="Identified risks")
    overall_risk_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Composite risk score between 0 and 10",
    )
    summary: str = Field(..., description="Plain-English summary of overall risk")


class SimplificationResult(BaseModel):
    """Result of the document simplification pass.

    Attributes:
        plain_english: Full document rewritten in plain English.
        key_points: Bullet-point list of the most important obligations or terms.
        unusual_clauses: Descriptions of clauses that are unusual or potentially unfavorable.
        document_type: Inferred document type (e.g. ``"NDA"``, ``"Employment Contract"``).
    """

    plain_english: str = Field(..., description="Document rewritten in plain English")
    key_points: list[str] = Field(
        default_factory=list, description="Key points from the document"
    )
    unusual_clauses: list[str] = Field(
        default_factory=list,
        description="Unusual or potentially unfavorable clauses",
    )
    document_type: str = Field(..., description="Inferred document type")


class FullAnalysisResult(BaseModel):
    """Combined response for the POST /analysis/{session_id}/full endpoint.

    Attributes:
        simplification: Plain-English simplification result.
        risk_analysis: Risk analysis result with individual risk entries.
    """

    simplification: SimplificationResult = Field(
        ..., description="Document simplification output"
    )
    risk_analysis: RiskAnalysisResult = Field(
        ..., description="Risk analysis output"
    )
