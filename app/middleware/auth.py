from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import traceback

from app.database.dependencies import get_admin_client, get_jwt_token

security = HTTPBearer()


async def get_current_user(
    jwt_token: str = Depends(get_jwt_token),
    db_client=Depends(get_admin_client),
):
    """
    Dependency that extracts and validates the current user from JWT token.
    
    Uses the admin client to validate the JWT with Supabase Auth (system operation).
    After validation, routes can decide whether to use admin or user-scoped client.
    
    Returns the authenticated user object from Supabase Auth.
    
    Args:
        jwt_token: The JWT token from Authorization header
        db_client: Admin client for JWT validation
    
    Returns:
        User object from Supabase Auth containing user ID and other claims
    """
    try:
        response = db_client.auth.get_user(jwt_token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token.",
            )

        return response.user

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )