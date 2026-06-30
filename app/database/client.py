from supabase import Client, create_client
from supabase.client import ClientOptions

from app.core.settings import settings


def create_admin_client() -> Client:
    """
    Factory function to create an admin Supabase client.
    
    Uses the service role key, which bypasses Row Level Security.
    
    Used for:
    - AI agent operations
    - Audit logging
    - Storage administration
    - Background jobs
    - OCR processing
    - PDF generation
    - Any operation requiring elevated privileges
    
    WARNING: This client can access all data. Use only for trusted operations.
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def create_user_client(jwt_token: str) -> Client:
    """
    Factory function to create a user-scoped Supabase client.
    
    Uses the anonymous key with a JWT token.
    This client respects Row Level Security policies.
    
    The JWT token determines which data the user can access based on:
    - User ID claims in the JWT
    - RLS policies in the database
    
    Used for:
    - User profile operations
    - User's own claims
    - User's own documents
    - Any operation respecting RLS
    
    Args:
        jwt_token: The authenticated user's JWT token from Supabase Auth
    
    Returns:
        A Supabase Client instance configured for the user context
    """
    options = ClientOptions()

    if jwt_token:
        options.headers["Authorization"] = f"Bearer {jwt_token}"

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options=options,
    )
