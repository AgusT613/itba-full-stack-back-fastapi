import uvicorn
from fastapi import FastAPI
from src.db.connection import create_db_and_tables
from contextlib import asynccontextmanager
from src.routers.routers import api_router
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)