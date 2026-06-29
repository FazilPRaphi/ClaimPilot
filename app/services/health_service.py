from supabase import Client

from app.services.base_service import BaseService


class HealthService(BaseService):
    """
    Service for health check operations.
    Verifies that critical systems are operational.
    """

    def check_database_connection(self) -> bool:
        """
        Check if the database is accessible.
        Returns True if connection is successful.
        """
        try:
            self.db_client.table("profiles").select("id").limit(1).execute()
            return True
        except Exception:
            return False
