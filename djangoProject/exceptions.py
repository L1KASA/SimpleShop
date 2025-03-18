class AppException(Exception):
    """Base exception class"""
    message = 'Internal Server Error'
    status_code = 500

    def __init__(self, message=None, details=None, status_code=None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        error_info = f"{self.message} (status_code={self.status_code})"
        if self.details:
            error_info += f": {self.details}"
        return error_info


class NotFoundError(AppException):
    """Resource Not Found exception"""

    message = 'Resource not found'
    status_code = 404


class ValidationError(AppException):
    """Validation Error exception"""
    message = 'Validation failed'
    status_code = 400


class CartOperationError(AppException):
    """Cart Operation Error exception"""
    message = 'Cart operation failed'
    status_code = 400


class InvalidJsonError(ValidationError):
    """Invalid JSON exception"""
    message = 'Invalid JSON format'


class ProductNotFoundError(NotFoundError):
    """Product Not Found exception"""
    message = 'Product Not Found'
