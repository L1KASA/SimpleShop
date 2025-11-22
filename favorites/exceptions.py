"""
Custom exceptions for favorites operations
"""


class FavoriteError(Exception):
    """Base exception for favorite-related errors"""
    pass


class FavoriteOperationError(FavoriteError):
    """Raised when a favorite operation fails"""
    pass
