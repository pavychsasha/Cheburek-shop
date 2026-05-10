from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response as StarletteResponse
from sqlalchemy import text

import uvicorn

from app.core.events import register_product_event_listeners
from app.core.config import settings
from app.core.models import sql_db_helper, mongo_db_helper, redis_db_helper
from app.core.services.translation import check_translation_service
from app.core.storage import check_media_storage, ensure_media_bucket, get_media_object
from app.api import router as router_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_db_helper.connect()
    await redis_db_helper.connect()
    await ensure_media_bucket()
    # startup
    register_product_event_listeners(sql_db_helper.session_factory)

    yield
    # shutdown
    await mongo_db_helper.dispose()
    await sql_db_helper.dispose()
    await redis_db_helper.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.session.secret_key)

app.include_router(router=router_v1, prefix=settings.api.prefix)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(response: Response):
    checks: dict[str, str] = {}

    try:
        async with sql_db_helper.session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:
        checks["postgres"] = f"error: {exc.__class__.__name__}"

    try:
        if mongo_db_helper.client is None:
            raise RuntimeError("MongoDB client is not initialized")
        await mongo_db_helper.client.admin.command("ping")
        checks["mongo"] = "ok"
    except Exception as exc:
        checks["mongo"] = f"error: {exc.__class__.__name__}"

    try:
        if redis_db_helper.redis is None:
            raise RuntimeError("Redis client is not initialized")
        await redis_db_helper.redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc.__class__.__name__}"

    try:
        await check_media_storage()
        checks["minio"] = "ok"
    except Exception as exc:
        checks["minio"] = f"error: {exc.__class__.__name__}"

    try:
        await check_translation_service()
        checks["translator"] = "ok" if settings.translation.enabled else "disabled"
    except Exception as exc:
        checks["translator"] = f"error: {exc.__class__.__name__}"

    is_healthy = all(value in {"ok", "disabled"} for value in checks.values())
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ok" if is_healthy else "degraded",
        "checks": checks,
    }


@app.get("/media/{object_name:path}", status_code=status.HTTP_200_OK)
async def get_public_media(object_name: str):
    payload, content_type = await get_media_object(object_name)
    return StarletteResponse(content=payload, media_type=content_type)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
