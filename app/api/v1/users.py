from fastapi import APIRouter, Depends
from supabase import Client

from app.database.dependencies import get_user_client
from app.middleware.auth import get_current_user
from app.services.user_service import UserService
from app.utils.responses import success_response

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user),
    db_client: Client = Depends(get_user_client),
):
    """
    Get current authenticated user information.
    
    Uses user-scoped client that respects Row Level Security.
    Only returns data the authenticated user is allowed to access.
    """
    user_service = UserService(db_client)
    
    return success_response(
        message="Authenticated user.",
        data={
            "id": current_user.id,
            "email": current_user.email,
        },
    )