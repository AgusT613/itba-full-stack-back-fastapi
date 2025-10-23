from fastapi import FastAPI
from db.connection import create_db_and_tables
from contextlib import asynccontextmanager
from routers.api import index


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(index.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
