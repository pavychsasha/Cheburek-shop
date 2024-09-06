from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import uvicorn

from core.config import settings
from api_v1 import router as router_v1
from users.views import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.include_router(users_router)


@app.get("/")
def hello_index():
    return {
        "message": "Hello index!",
    }


@app.get("/hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}!"}


@app.get("/calc/add/")
def add(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }
