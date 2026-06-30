from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.logger import get_logger
from app.database.dependencies import get_user_client
from app.exceptions import DatabaseError, NotFoundError, ValidationError
from app.middleware.auth import get_current_user
from app.schemas.claim import ClaimCreateRequest, ClaimUpdateRequest
from app.schemas.response import APIResponse
from app.services.claim_service import ClaimService
from app.utils.responses import success_response

router = APIRouter(prefix="/claims", tags=["Claims"])
logger = get_logger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_claim(
    request: ClaimCreateRequest,
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """Create a draft claim for the authenticated user."""
    claim_service = ClaimService(db_client)
    try:
        claim = claim_service.create_claim(
            user_id=current_user.id,
            claim_data=request.model_dump(),
        )
        return success_response(message="Claim created successfully.", data=claim)
    except Exception as exc:
        _raise_http_exception(exc)


@router.get("")
async def list_claims(
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """List non-deleted claims for the authenticated user."""
    claim_service = ClaimService(db_client)
    try:
        claims = claim_service.list_claims(user_id=current_user.id)
        return success_response(message="Claims retrieved successfully.", data=claims)
    except Exception as exc:
        _raise_http_exception(exc)


@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """Retrieve a single non-deleted claim."""
    claim_service = ClaimService(db_client)
    try:
        claim = claim_service.get_claim(claim_id)
        return success_response(message="Claim retrieved successfully.", data=claim)
    except Exception as exc:
        _raise_http_exception(exc)


@router.patch("/{claim_id}")
async def update_claim(
    claim_id: str,
    request: ClaimUpdateRequest,
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """Update user-editable fields on a claim."""
    claim_service = ClaimService(db_client)
    try:
        claim = claim_service.update_claim(
            claim_id=claim_id,
            claim_data=request.model_dump(exclude_unset=True),
        )
        return success_response(message="Claim updated successfully.", data=claim)
    except Exception as exc:
        _raise_http_exception(exc)
@router.post("/{claim_id}/analyze")
async def analyze_claim(
    claim_id: str,
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """
    Analyze a claim using AI.

    Workflow:

    1. Load all OCR text for the claim.
    2. Merge OCR text.
    3. Send it to Groq.
    4. Save AI results.
    5. Return analysis.
    """

    claim_service = ClaimService(db_client)

    try:

        analysis = claim_service.analyze_claim(
            claim_id
        )

        return success_response(
            message="Claim analyzed successfully.",
            data=analysis,
        )

    except Exception as exc:

        _raise_http_exception(exc)

@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: str,
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
) -> APIResponse:
    """Soft delete a claim."""
    claim_service = ClaimService(db_client)
    try:
        claim = claim_service.delete_claim(claim_id)
        return success_response(message="Claim deleted successfully.", data=claim)
    except Exception as exc:
        _raise_http_exception(exc)


def _raise_http_exception(exc: Exception) -> None:
    """Convert business exceptions into HTTP exceptions.

    Always logs the full traceback so the root cause is visible in server logs.
    """
    import traceback as _tb
    _tb.print_exc()
    logger.error("Claims API error: %s", exc, exc_info=True)

    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, DatabaseError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    # Unexpected exception: expose type + message for debuggability.
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{type(exc).__name__}: {exc}",
    ) from exc

