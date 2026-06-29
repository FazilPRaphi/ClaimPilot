from fastapi import APIRouter

from app.core.settings import settings
from app.utils.responses import success_response

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
)
async def health_check():

    return success_response(
        message="API is healthy.",
        data={
            "environment": settings.APP_ENV,
            "version": settings.APP_VERSION,
        },
    )