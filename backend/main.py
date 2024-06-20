from fastapi import FastAPI
from fastapi.routing import APIRoute

from backend.api.v1.main import api_router
from backend.core.config import settings
from backend.core.db import init_db


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


init_db()
app.include_router(api_router, prefix=settings.API_V1_STR)
