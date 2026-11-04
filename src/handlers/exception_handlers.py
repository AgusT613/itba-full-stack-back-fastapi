from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from src.exceptions.banking_exceptions import BankingException


async def banking_exception_handler(request: Request, exc: BankingException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(BankingException, banking_exception_handler)
