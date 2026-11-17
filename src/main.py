from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.constants.constants import ENVIRONMENT, HOMEBANKING_FRONTEND_URL
from src.db.connection import cleanup_prod_database, create_db_and_tables
from src.db.init_db import init_production_db
from src.db.seed import seed_dev_database
from src.handlers import register_exception_handlers
from src.routers.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    if ENVIRONMENT in ("development", "dev"):
        seed_dev_database()
    elif ENVIRONMENT in ("production", "prod"):
        init_production_db()
    yield
    if ENVIRONMENT in ("production", "prod"):
        cleanup_prod_database()



origins = [HOMEBANKING_FRONTEND_URL]

app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
