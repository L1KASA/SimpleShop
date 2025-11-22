import logging

from django.http import HttpRequest

from favorites.FavoriteFactory import FavoriteFactory
from favorites.exceptions import FavoriteOperationError
from myapp.models import Product

logger = logging.getLogger(__name__)


class FavoriteService:
    @staticmethod
    def toggle_favorite(request: HttpRequest, product_id: int):
        favorite_handler = FavoriteFactory.build_favorite(request)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found")
            return {
                'success': False,
                'message': f'Product {product_id} not found',
            }

        try:
            # Check current state
            is_currently_favorite = favorite_handler.is_favorite(product_id)

            if is_currently_favorite:
                # Remove from favorites
                return favorite_handler.remove_from_favorites(product_id)
            else:
                # Add to favorites
                return favorite_handler.add_to_favorites(product)

        except FavoriteOperationError as e:
            logger.error(f"Error toggling favorite: {str(e)}")
            return {
                'success': False,
                'message': 'Error toggling favorite',
            }

    @staticmethod
    def add_to_favorites(request: HttpRequest, product_id: int):
        favorite_handler = FavoriteFactory.build_favorite(request)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.warning(f"Product {product_id} not found")
            return {
                'success': False,
                'message': f'Product {product_id} not found',
            }

        try:
            return favorite_handler.add_to_favorites(product)
        except FavoriteOperationError as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return {
                'success': False,
                'message': 'Error adding to favorites',
            }

    @staticmethod
    def remove_from_favorites(request: HttpRequest, product_id: int):
        favorite_handler = FavoriteFactory.build_favorite(request)

        try:
            return favorite_handler.remove_from_favorites(product_id)
        except FavoriteOperationError as e:
            logger.error(f"Error removing from favorites: {str(e)}")
            return {
                'success': False,
                'message': 'Error removing from favorites',
            }

    @staticmethod
    def get_favorites(request):
        favorite_handler = FavoriteFactory.build_favorite(request)
        return favorite_handler.get_favorites()

    @staticmethod
    def get_favorites_ids(request):
        favorite_handler = FavoriteFactory.build_favorite(request)
        favorites_data = favorite_handler.get_favorites()
        return favorites_data.get('favorites_ids', [])

    @staticmethod
    def is_favorite(request, product_id: int):
        favorite_handler = FavoriteFactory.build_favorite(request)
        return favorite_handler.is_favorite(product_id)

    @staticmethod
    def get_favorites_count(request: HttpRequest) -> int:
        favorite_handler = FavoriteFactory.build_favorite(request)
        return favorite_handler.get_favorites_count()
