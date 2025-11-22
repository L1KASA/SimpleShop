from django.http import HttpRequest

from favorites.FavoritesBase import FavoriteDB, FavoriteSession


class FavoriteFactory:
    """Factory for creating appropriate favorite handler based on authentication"""

    @staticmethod
    def build_favorite(request: HttpRequest):
        """Build favorite handler - DB for authenticated, Session for anonymous"""
        if request.user.is_authenticated:
            return FavoriteDB(request)
        else:
            return FavoriteSession(request)
