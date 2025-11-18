from fastapi import FastAPI
from db.connection import create_db_and_tables
from contextlib import asynccontextmanager
from routers.routers import api_router
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
async def read_root():
    return {"Hello": "FastAPI"}
