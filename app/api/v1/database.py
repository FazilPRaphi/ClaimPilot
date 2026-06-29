from fastapi import APIRouter

from app.database.client import supabase
from app.utils.responses import success_response

router = APIRouter()


@router.get("/database")
async def database_status():
    try:
        supabase.table("profiles").select("id").limit(1).execute()

        return success_response(
            message="Database connection successful."
        )

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }