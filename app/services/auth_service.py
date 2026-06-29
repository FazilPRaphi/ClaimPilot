from supabase import Client

from app.services.base_service import BaseService
from app.services.profile_service import ProfileService


class AuthService(BaseService):
    """
    Service for handling authentication operations.
    Receives database client as a dependency.
    """

    def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ):
        """Register a new user and create their profile."""
        response = self.db_client.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        user = response.user

        if user:
            profile_service = ProfileService(self.db_client)
            profile_service.create_profile(
                user.id,
                email,
                full_name,
            )

        return response

    def login(
        self,
        email: str,
        password: str,
    ):
        """Authenticate user with email and password."""
        return self.db_client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )