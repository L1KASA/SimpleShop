"""
Custom exceptions for cart operations
"""


class CartError(Exception):
    """Base exception for cart-related errors"""
    pass


class ProductNotFoundError(CartError):
    """Raised when a product is not found"""
    pass


class CartOperationError(CartError):
    """Raised when a cart operation fails"""
    pass
