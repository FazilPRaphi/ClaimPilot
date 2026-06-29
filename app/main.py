from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import api_router
from app.core.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Claim Processing Platform",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered Claim Processing Platform",
        routes=app.routes,
    )

    components = openapi_schema.get("components", {}).get("schemas", {})
    for schema in components.values():
        if schema.get("type") == "object" and isinstance(schema.get("properties"), dict):
            for prop in schema["properties"].values():
                if prop.get("type") == "string" and prop.get("contentMediaType"):
                    prop.setdefault("format", "binary")

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Welcome to ClaimPilot API"
    }