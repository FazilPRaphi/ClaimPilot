from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from app.database.client import create_admin_client, create_user_client

security = HTTPBearer()


def get_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extracts the JWT token from the Authorization header.
    
    Used internally by dependencies to obtain the user's JWT.
    Can be used by any dependency that needs to validate or scope requests.
    """
    return credentials.credentials


def get_admin_client() -> Client:
    """
    FastAPI dependency that provides an admin Supabase client.
    
    This client uses the service role key and bypasses Row Level Security.
    
    Inject into route handlers or services that need elevated privileges:
    - AI agents
    - Audit logging
    - Storage administration
    - Background jobs
    
    Example:
        @router.post("/admin/logs")
        async def log_event(db = Depends(get_admin_client)):
            db.table("audit_logs").insert({...}).execute()
    """
    return create_admin_client()


def get_user_client(
    jwt_token: str = Depends(get_jwt_token),
) -> Client:
    """
    FastAPI dependency that provides a user-scoped Supabase client.
    
    This client respects Row Level Security based on the user's JWT token.
    
    Automatically extracts the JWT from the Authorization header and creates
    a client scoped to that user's context.
    
    Inject into route handlers or services that operate on behalf of users:
    - User profile operations
    - User's claims
    - User's documents
    - Any operation respecting user's RLS permissions
    
    Example:
        @router.get("/me")
        async def get_profile(db = Depends(get_user_client)):
            profile = db.table("profiles").select("*").single().execute()
            return profile
    """
    return create_user_client(jwt_token)


# Alias for backward compatibility and clarity
get_current_user_client = get_user_client

