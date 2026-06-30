"""
Document schemas for ClaimPilot.

These schemas define the request and response models used by the
Document Management module.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """
    Represents a document stored in ClaimPilot.
    """

    id: str
    claim_id: str
    file_name: str
    storage_path: str
    document_type: str
    upload_status: str

    extracted_text: str | None = None
    ocr_confidence: float | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """
    Response model for multiple uploaded documents.
    """

    documents: List[DocumentResponse]


class DeleteDocumentResponse(BaseModel):
    """
    Response returned after a successful soft delete.
    """

    success: bool
    message: str


class UploadDocumentResult(BaseModel):
    """
    Internal response after a successful upload.

    This model is used by the service layer before the API response
    wrapper formats the final HTTP response.
    """

    document: DocumentResponse


class OCRResultResponse(BaseModel):
    """
    Response returned after OCR extraction.
    """

    document: DocumentResponse