from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Claim Processing Platform",
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Welcome to ClaimPilot API"
    }