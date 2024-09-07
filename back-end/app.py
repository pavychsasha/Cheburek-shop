from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import uvicorn

from core.config import settings
from core.models import db_helper
from api import router as router_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(router=router_v1, prefix=settings.api.prefix)
