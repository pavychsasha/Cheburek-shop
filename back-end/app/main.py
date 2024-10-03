from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import uvicorn

from app.core.config import settings
from app.core.models import sql_db_helper, mongo_db_helper
from app.api import router as router_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_db_helper.connect()
    # startup
    yield
    # shutdown
    await mongo_db_helper.dispose()
    await sql_db_helper.dispose()


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

origins = ["http://react:5173", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.session.secret_key)

app.include_router(router=router_v1, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
