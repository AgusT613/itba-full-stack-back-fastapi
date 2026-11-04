class BankingException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class EntityNotFoundError(BankingException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class InsufficientFundsError(BankingException):
    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, status_code=400)


class DuplicateResourceError(BankingException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=400)


class UnauthorizedOperationError(BankingException):
    def __init__(self, message: str = "Operation not allowed"):
        super().__init__(message, status_code=403)


class InvalidOperationError(BankingException):
    def __init__(self, message: str = "Invalid operation"):
        super().__init__(message, status_code=400)
