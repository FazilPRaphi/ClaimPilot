from fastapi import APIRouter, Depends
from supabase import Client

from app.database.dependencies import get_admin_client
from app.services.health_service import HealthService
from app.utils.responses import error_response, success_response

router = APIRouter()


@router.get("/database")
async def database_status(db_client: Client = Depends(get_admin_client)):
    """
    Check database connection status.
    
    Uses admin client to verify database connectivity.
    This is a system health check operation.
    """
    try:
        health_service = HealthService(db_client)
        is_healthy = health_service.check_database_connection()

        if is_healthy:
            return success_response(
                message="Database connection successful."
            )
        else:
            return error_response(
                message="Database connection failed."
            )

    except Exception as e:
        return error_response(
            message=str(e)
        )