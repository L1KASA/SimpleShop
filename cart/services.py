import logging

from django.http import HttpRequest, Http404

from cart.CartFactory import CartFactory
from cart.exceptions import CartOperationError, ProductNotFoundError
from myapp.models import Product

logger = logging.getLogger(__name__)


class CartService:
    @staticmethod
    def save_cart(request: HttpRequest):
        """Save cart"""
        cart_handler = CartFactory.build_cart(request)
        return cart_handler.save_cart()

    @staticmethod
    def add_to_cart(request: HttpRequest, product_id: int):
        """Add product to cart"""
        cart_handler = CartFactory.build_cart(request)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ProductNotFoundError(f"Product with id {product_id} not found")
        
        try:
            return cart_handler.add_to_cart(product)
        except CartOperationError as e:
            logger.error(f"Error adding product to cart: {str(e)}")
            raise

    @staticmethod
    def remove_from_cart(request: HttpRequest, product_id: int):
        """Remove product from cart"""
        cart_handler = CartFactory.build_cart(request)
        try:
            return cart_handler.remove_from_cart(product_id)
        except CartOperationError as e:
            logger.error(f"Error removing products from cart: {str(e)}")
            raise

    @staticmethod
    def update_quantity(request, product_id, quantity_change):
        """Update product quantity"""
        cart_handler = CartFactory.build_cart(request)

        try:
            return cart_handler.update_quantity(product_id, quantity_change)
        except CartOperationError as e:
            logger.error(f"Error updating product quantity: {str(e)}")
            raise

    @staticmethod
    def get_cart_items(request):
        """Get cart data for template"""
        cart_handler = CartFactory.build_cart(request)
        return cart_handler.get_cart_items()
