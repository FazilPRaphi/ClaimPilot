from supabase import Client

from app.services.base_service import BaseService


class ProfileService(BaseService):
    """
    Service for handling user profile operations.
    Receives database client as a dependency.
    """

    def create_profile(
        self,
        user_id: str,
        email: str,
        full_name: str,
    ):
        """Create a new user profile."""
        return (
            self.db_client
            .table("profiles")
            .insert(
                {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "role": "user",
                }
            )
            .execute()
        )

    def get_profile(self, user_id: str):
        """Retrieve a user profile by ID."""
        return (
            self.db_client
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )