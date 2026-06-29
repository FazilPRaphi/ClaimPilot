from supabase import Client

from app.services.base_service import BaseService
from app.services.profile_service import ProfileService


class UserService(BaseService):
    """
    Service for handling user-related operations.
    Manages user profiles and user-specific queries.
    """

    def get_profile(self, user_id: str):
        """Retrieve a user's profile."""
        profile_service = ProfileService(self.db_client)
        return profile_service.get_profile(user_id)
