import logging
from abc import abstractmethod, ABC

from django.http import HttpRequest
from typing import Any, Dict

from favorites.models import Favorite
from favorites.exceptions import FavoriteOperationError
from myapp.models import Product

logger = logging.getLogger(__name__)


class FavoriteInterface(ABC):
    @abstractmethod
    def add_to_favorites(self, product: Product) -> Dict[str, Any]:
        """Add product to favorites"""
        pass

    @abstractmethod
    def remove_from_favorites(self, product_id: int) -> Dict[str, Any]:
        """Remove product from favorites"""
        pass

    @abstractmethod
    def is_favorite(self, product_id: int) -> bool:
        """Check if product is in favorites"""
        pass

    @abstractmethod
    def get_favorites(self) -> Dict[str, Any]:
        """Get all favorite products"""
        pass

    @abstractmethod
    def get_favorites_count(self) -> int:
        """Get count of favorite items"""
        pass

    @abstractmethod
    def clear_favorites(self) -> Dict[str, Any]:
        """Clear all favorites"""
        pass


class FavoriteDB(FavoriteInterface):
    """Database-based favorites for authenticated users"""

    def __init__(self, request: HttpRequest) -> None:
        self._request = request
        self._user = request.user

    def add_to_favorites(self, product: Product) -> Dict[str, Any]:
        """Add product to database favorites"""
        try:
            favorite, created = Favorite.objects.get_or_create(
                user=self._user,
                product=product
            )

            if created:
                logger.info(f"Added product {product.id} to favorites for user {self._user.id}")
                message = 'Added to favorites'
            else:
                logger.info(f"Product {product.id} already in favorites for user {self._user.id}")
                message = 'Already in favorites'

            return {
                'success': True,
                'message': message,
                'is_favorite': True,
                'favorites_count': self.get_favorites_count(),
            }

        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to add to favorites: {str(e)}") from e

    def remove_from_favorites(self, product_id: int) -> Dict[str, Any]:
        """Remove product from database favorites"""
        try:
            deleted_count, _ = Favorite.objects.filter(
                user=self._user,
                product_id=product_id
            ).delete()

            if deleted_count > 0:
                logger.info(f"Removed product {product_id} from favorites for user {self._user.id}")
                message = 'Removed from favorites'
            else:
                logger.warning(f"Product {product_id} not in favorites for user {self._user.id}")
                message = 'Not in favorites'

            return {
                'success': True,
                'message': message,
                'is_favorite': False,
                'favorites_count': self.get_favorites_count(),
            }

        except Exception as e:
            logger.error(f"Error removing from favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to remove from favorites: {str(e)}") from e

    def is_favorite(self, product_id: int) -> bool:
        """Check if product is in database favorites"""
        return Favorite.objects.filter(user=self._user, product_id=product_id).exists()

    def get_favorites(self) -> Dict[str, Any]:
        """Get all favorite products from database"""
        try:
            favorites = Favorite.objects.filter(user=self._user).select_related('product')
            products = [fav.product for fav in favorites]

            return {
                'products': products,
                'favorites_count': len(products),
                'favorites_ids': [p.id for p in products],
                'in_db': True,
            }

        except Exception as e:
            logger.error(f"Error getting favorites from DB: {str(e)}")
            raise FavoriteOperationError(f"Failed to get favorites: {str(e)}") from e

    def get_favorites_count(self) -> int:
        """Get count of favorite items in database"""
        return Favorite.objects.filter(user=self._user).count()

    def clear_favorites(self) -> Dict[str, Any]:
        """Clear all database favorites"""
        try:
            deleted_count, _ = Favorite.objects.filter(user=self._user).delete()
            logger.info(f"Cleared {deleted_count} favorites for user {self._user.id}")

            return {
                'success': True,
                'message': f'Cleared {deleted_count} favorites',
            }

        except Exception as e:
            logger.error(f"Error clearing favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to clear favorites: {str(e)}") from e

    def bulk_create_items(self, favorite_items):
        """Bulk create favorite items"""
        try:
            Favorite.objects.bulk_create(favorite_items, ignore_conflicts=True)
            logger.info(f"Bulk created {len(favorite_items)} favorite items")
        except Exception as e:
            logger.error(f"Error bulk creating favorite items: {str(e)}")
            raise FavoriteOperationError(f"Failed to bulk create favorites: {str(e)}") from e


class FavoriteSyncService:
    """Service for synchronizing favorites between session and database"""

    @staticmethod
    def sync_session_to_db(request):
        """
        Synchronize favorites from session to database after user login.
        Transfers all items from FavoriteSession to FavoriteDB.
        """
        session_favorites = FavoriteSession(request)
        session_data = session_favorites._favorites

        if not session_data:
            logger.info("No items in session favorites to sync")
            return

        product_ids = [int(pid) for pid in session_data]

        products = Product.objects.filter(id__in=product_ids)
        products_dict = {product.id: product for product in products}

        existing_favorites = Favorite.objects.filter(
            user=request.user,
            product_id__in=product_ids
        ).values_list('product_id', flat=True)
        existing_set = set(existing_favorites)

        favorites_to_create = []

        for product_id in product_ids:
            product = products_dict.get(product_id)

            if not product:
                logger.warning(f"Product {product_id} not found, skipping sync")
                continue

            if product_id in existing_set:
                continue

            favorites_to_create.append(
                Favorite(user=request.user, product=product)
            )

        db_favorites = FavoriteDB(request)

        if favorites_to_create:
            db_favorites.bulk_create_items(favorites_to_create)

        synced_count = len(favorites_to_create)

        # Clear session favorites after successful sync
        if synced_count > 0:
            session_favorites.clear_favorites()
            logger.info(f"Successfully synced {synced_count} items from session to DB favorites")


class FavoriteSession(FavoriteInterface):
    def __init__(self, request: HttpRequest) -> None:
        self._request = request
        self._session = request.session
        self._favorites = set(self._session.get('favorites', []))

    def add_to_favorites(self, product: Product) -> Dict[str, Any]:
        """Add product to session favorites"""
        try:
            product_id = product.id
            was_added = product_id not in self._favorites

            self._favorites.add(product_id)
            self._save_to_session()

            return {
                'success': True,
                'message': 'Added to favorites' if was_added else 'Already in favorites',
                'is_favorite': True,
                'favorites_count': self.get_favorites_count(),
            }

        except Exception as e:
            logger.error(f"Error adding to session favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to add to favorites: {str(e)}") from e

    def remove_from_favorites(self, product_id: int) -> Dict[str, Any]:
        """Remove product from session favorites"""
        try:
            was_removed = product_id in self._favorites

            self._favorites.discard(product_id)
            self._save_to_session()

            return {
                'success': True,
                'message': 'Removed from favorites' if was_removed else 'Not in favorites',
                'is_favorite': False,
                'favorites_count': self.get_favorites_count(),
            }

        except Exception as e:
            logger.error(f"Error removing from session favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to remove from favorites: {str(e)}") from e

    def is_favorite(self, product_id: int) -> bool:
        """Check if product is in session favorites"""
        return product_id in self._favorites

    def get_favorites(self) -> Dict[str, Any]:
        """Get all favorite products from session"""
        try:
            if not self._favorites:
                return {
                    'products': [],
                    'favorites_count': 0,
                    'favorites_ids': [],
                    'in_db': False,
                }

            product_ids = list(self._favorites)
            products = Product.objects.filter(id__in=product_ids)

            return {
                'products': list(products),
                'favorites_count': len(products),
                'favorites_ids': product_ids,
                'in_db': False,
            }

        except Exception as e:
            logger.error(f"Error getting session favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to get favorites: {str(e)}") from e

    def get_favorites_count(self) -> int:
        """Get count of favorite items in session"""
        return len(self._favorites)

    def clear_favorites(self) -> Dict[str, Any]:
        """Clear all session favorites"""
        try:
            count = len(self._favorites)
            self._favorites.clear()
            self._save_to_session()

            logger.info(f"Cleared {count} session favorites")

            return {
                'success': True,
                'message': f'Cleared {count} favorites',
            }

        except Exception as e:
            logger.error(f"Error clearing session favorites: {str(e)}")
            raise FavoriteOperationError(f"Failed to clear favorites: {str(e)}") from e

    def _save_to_session(self):
        """Save favorites set to session"""
        self._session['favorites'] = list(self._favorites)
        self._session.modified = True
