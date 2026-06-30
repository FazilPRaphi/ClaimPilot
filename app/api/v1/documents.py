"""
Document API routes.

Handles document upload and management.
"""

import traceback
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.core.logger import get_logger
from app.database.dependencies import (
    get_admin_client,
    get_current_user_client,
)
from app.exceptions import (
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from app.middleware.auth import get_current_user
from app.services.document_service import DocumentService
from app.utils.responses import success_response

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

logger = get_logger(__name__)


def _raise_http_exception(exc: Exception) -> None:
    """
    Temporary debugging exception handler.
    Prints the complete traceback and exposes the original exception.
    """

    traceback.print_exception(
        type(exc),
        exc,
        exc.__traceback__,
    )

    logger.exception("Unhandled exception during document request.")

    if isinstance(exc, ValidationError):
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if isinstance(exc, NotFoundError):
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if isinstance(exc, DatabaseError):
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    raise HTTPException(
        status_code=500,
        detail=f"{type(exc).__name__}: {exc}",
    ) from exc


@router.post("/claims/{claim_id}")
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    current_user=Depends(get_current_user),

    # TEMPORARY:
    # Use the admin client to verify whether Storage RLS
    # is the source of the failure.
    db=Depends(get_admin_client),
):
    """
    Upload a document for a claim.
    """

    try:
        service = DocumentService(db)

        document = await service.upload_document(
            user_id=current_user.id,
            claim_id=claim_id,
            file=file,
            document_type=document_type,
        )

        return success_response(
            message="Document uploaded successfully.",
            data=document.model_dump(),
        )

    except Exception as exc:
        _raise_http_exception(exc)


@router.get("/claims/{claim_id}")
async def list_documents(
    claim_id: str,
    db=Depends(get_current_user_client),
):
    """
    List all documents belonging to a claim.
    """

    try:
        service = DocumentService(db)

        documents = service.list_documents(claim_id)

        return success_response(
            message="Documents retrieved successfully.",
            data=documents.data,
        )

    except Exception as exc:
        _raise_http_exception(exc)


@router.get("/{document_id}")
async def get_document(
    document_id: UUID,
    db=Depends(get_current_user_client),
):
    """
    Retrieve a single document.
    """

    try:
        service = DocumentService(db)

        document = service.get_document(document_id)

        return success_response(
            message="Document retrieved successfully.",
            data=document.data,
        )

    except Exception as exc:
        _raise_http_exception(exc)
@router.post("/{document_id}/extract")

async def extract_document_text(
    document_id: UUID,
    db=Depends(get_current_user_client),
):
    """
    Run OCR on an uploaded document.
    """

    service = DocumentService(db)

    try:

        document = await service.extract_document_text(
            document_id
        )

        return success_response(
            message="OCR extraction completed successfully.",
            data=document.model_dump(),
        )

    except Exception as exc:
        _raise_http_exception(exc)

@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_current_user_client),
):
    """
    Generate a signed download URL for a document.
    """

    try:
        service = DocumentService(db)

        signed_url = service.generate_download_url(document_id)

        return success_response(
            message="Download URL generated successfully.",
            data={
                "download_url": signed_url,
            },
        )

    except Exception as exc:
        _raise_http_exception(exc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_current_user_client),
):
    """
    Delete a document.
    """

    try:
        service = DocumentService(db)

        service.delete_document(document_id)

        return success_response(
            message="Document deleted successfully.",
        )

    except Exception as exc:
        _raise_http_exception(exc)
