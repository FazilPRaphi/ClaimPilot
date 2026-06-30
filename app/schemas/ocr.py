"""
OCR schemas for ClaimPilot.

These schemas define the internal models used by the OCR
pipeline and AI document processing.
"""

from pydantic import BaseModel, ConfigDict


class OCRResult(BaseModel):
    """
    Result returned after a successful OCR operation.
    """

    text: str
    confidence: float
    page_count: int
    processing_time_ms: float

    model_config = ConfigDict(from_attributes=True)