from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    status,
    UploadFile,
)

from app.core.logger import get_logger
from app.database.dependencies import get_current_user_client
from app.exceptions import DatabaseError, NotFoundError, ValidationError
from app.middleware.auth import get_current_user
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.utils.responses import success_response

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)
logger = get_logger(__name__)


def _raise_http_exception(exc: Exception) -> None:
    """Convert business exceptions into HTTP exceptions."""
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, DatabaseError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    logger.error("Unexpected documents API error: %s", exc)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error.",
    ) from exc


@router.post(
    "/claims/{claim_id}",
    response_model=None,
)
async def upload_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    current_user=Depends(get_current_user),
    db=Depends(get_current_user_client),
):
    """
    Upload a document for a claim.
    """

    service = DocumentService(db)
    try:
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


@router.get(
    "/claims/{claim_id}",
)
async def list_documents(
    claim_id: str,
    db=Depends(get_current_user_client),
):
    """
    List all documents belonging to a claim.
    """

    service = DocumentService(db)
    try:
        documents = service.list_documents(claim_id)
        return success_response(
            message="Documents retrieved successfully.",
            data=documents.data,
        )
    except Exception as exc:
        _raise_http_exception(exc)


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db=Depends(get_current_user_client),
):
    """
    Retrieve a single document.
    """

    service = DocumentService(db)
    try:
        document = service.get_document(document_id)
        return success_response(
            message="Document retrieved successfully.",
            data=document.data,
        )
    except Exception as exc:
        _raise_http_exception(exc)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db=Depends(get_current_user_client),
):
    """
    Soft delete a document.
    """

    service = DocumentService(db)
    try:
        service.delete_document(document_id)
        return success_response(
            message="Document deleted successfully.",
        )
    except Exception as exc:
        _raise_http_exception(exc)