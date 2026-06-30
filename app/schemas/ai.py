"""
AI schemas for ClaimPilot.

These schemas define the structured responses returned
by the AI analysis pipeline.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class StructuredClaimData(BaseModel):
    """
    Structured information extracted from OCR text.
    """

    claim_type: str | None = None
    claimant_name: str | None = None
    hospital_name: str | None = None
    invoice_number: str | None = None
    policy_number: str | None = None
    date: str | None = None
    amount: float | None = None
    currency: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AIAnalysisResponse(BaseModel):
    """
    Complete AI analysis result.
    """

    summary: str

    structured_data: StructuredClaimData

    important_entities: List[str] = Field(
        default_factory=list
    )

    missing_information: List[str] = Field(
        default_factory=list
    )

    readiness_score: int = Field(
        ge=0,
        le=100,
    )

    model_config = ConfigDict(from_attributes=True)