from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.database.dependencies import get_admin_client
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
)
from app.services.auth_service import AuthService
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(
    request: RegisterRequest,
    db_client: Client = Depends(get_admin_client),
):
    """
    Register a new user.
    
    Creates a new user in Supabase Auth and initializes their profile.
    Uses admin client since this is a user creation operation (system-level).
    """
    try:
        auth_service = AuthService(db_client)
        auth_service.register(
            request.email,
            request.password,
            request.full_name,
        )
        return success_response(
            message="Registration successful."
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/login")
async def login(
    request: LoginRequest,
    db_client: Client = Depends(get_admin_client),
):
    """
    Authenticate a user and return session.
    
    Validates credentials and returns a JWT session token.
    Uses admin client for the authentication operation (system-level).
    """
    try:
        auth_service = AuthService(db_client)
        session = auth_service.login(
            request.email,
            request.password,
        )

        return success_response(
            message="Login successful.",
            data=session.model_dump(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )