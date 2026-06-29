"""
Pydantic schemas for claims API contracts.
"""

from pydantic import BaseModel, ConfigDict, Field


class ClaimCreateRequest(BaseModel):
    """Request body for creating a claim."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    claim_type: str = Field(..., min_length=1, max_length=100)


class ClaimUpdateRequest(BaseModel):
    """Request body for updating user-editable claim fields."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    claim_type: str | None = Field(default=None, min_length=1, max_length=100)


class ClaimResponse(BaseModel):
    """Response model for claim records."""

    id: str
    claim_number: str
    user_id: str
    title: str
    description: str | None = None
    claim_type: str
    status: str
    current_stage: str
    readiness_score: int | None = None
    confidence_score: int | None = None
    ai_summary: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    deleted_at: str | None = None

    model_config = ConfigDict(from_attributes=True)
