import logging
from abc import abstractmethod, ABC

from django.db.models import Sum
from django.http import HttpRequest
from typing import Any, Dict

from cart.models import Cart
from cart.exceptions import CartOperationError
from myapp.models import Product

logger = logging.getLogger(__name__)


class CartInterface(ABC):
    """Abstract base class for cart operations"""

    @abstractmethod
    def add_to_cart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_quantity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def remove_from_cart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_cart_count(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_cart_items(self, *args: Any, **kwargs: Any) -> int:
        pass

    @abstractmethod
    def clear_cart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save_cart(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        pass


class CartCalculatorMixin:
    """Mixin for centralized cart calculation logic"""

    @staticmethod
    def _build_cart_item(product, quantity, price):
        """Build a standardized cart item dictionary"""
        from decimal import Decimal
        item_total = Decimal(str(price)) * quantity
        return {
            'product': product,
            'quantity': quantity,
            'total_price': item_total,
            'price': Decimal(str(price)),
            'image': product.image.url if product.image else '',
            'name': product.name
        }

    @staticmethod
    def _calculate_total_price(cart_items):
        """Calculate total price from cart items list"""
        from decimal import Decimal
        return sum(item['total_price'] for item in cart_items)


class CartDB(CartInterface, CartCalculatorMixin):
    def __init__(self, request: HttpRequest) -> None:
        self._request = request
        self._user = request.user

    def add_to_cart(self, product: Product):
        """Add product to database cart"""
        try:
            cart_item, created = Cart.objects.get_or_create(
                user=self._user,
                product=product,
                defaults={'quantity': 0}
            )

            cart_item.quantity += 1
            cart_item.save()

            if created:
                logger.info(f"Created new cart item: {cart_item}")
            else:
                logger.info(f"Updated existing cart item: {cart_item.quantity}")

            cart_count = self.get_cart_count()

            return {
                'success': True,
                'message': 'Product added to cart',
                'cart_count': cart_count,
                'in_db': True,
            }

        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            raise CartOperationError(f"Failed to add product to cart: {str(e)}") from e

    def update_quantity(self, product_id: int, quantity_change: int):
        """Update product quantity"""
        try:
            cart = Cart.objects.filter(user=self._user, product_id=product_id).first()
            if not cart:
                return {
                    'success': False,
                    'message': 'Product not found in cart'
                }

            new_quantity = cart.quantity + quantity_change

            if new_quantity <= 0:
                cart.delete()
                item_quantity = 0
            else:
                cart.quantity = new_quantity
                cart.save()
                item_quantity = new_quantity

            return {
                'success': True,
                'message': 'Quantity updated',
                'cart_count': self.get_cart_count(),
                'item_quantity': item_quantity
            }
        except Exception as e:
            logger.error(f"Error updating product quantity: {str(e)}")
            raise CartOperationError(f"Failed to update quantity: {str(e)}") from e

    def remove_from_cart(self, product_id: int):
        try:
            cart = Cart.objects.filter(user=self._user, product_id=product_id).first()

            if cart is None:
                return {
                    'success': False,
                    'message': 'Product not found in cart',
                    'cart_count': self.get_cart_count(),
                }

            cart.delete()

            cart_count = self.get_cart_count()

            return {
                'success': True,
                'message': 'Product removed from cart',
                'cart_count': cart_count,
            }
        except Cart.DoesNotExist:
            logger.warning(f"Product {product_id} not found in cart for user {self._user}")
            return {
                'success': False,
                'message': 'Product not found in cart',
            }

    def get_cart_count(self):
        """Get total items count from database"""
        try:
            result = Cart.objects.filter(user=self._user).aggregate(total=Sum('quantity'))
            return result['total'] or 0
        except Exception as e:
            logger.error(e)
            return 0

    def get_cart_items(self):
        """Get cart items for template from database"""
        from decimal import Decimal
        from django.db.models import F, Sum
        try:
            cart = Cart.objects.filter(user=self._user).select_related('product')
            cart_items = []

            for cart_item in cart:
                cart_items.append(
                    self._build_cart_item(
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                )

            total_result = Cart.objects.filter(user=self._user).aggregate(
                total=Sum(F('quantity') * F('product__price'))
            )
            total_price = total_result['total'] or Decimal('0.00')

            return {
                'cart_items': cart_items,
                'total_price': total_price,
                'cart_count': self.get_cart_count(),
                'in_db': True
            }

        except Exception as e:
            logger.error(f"Error getting cart data from DB: {str(e)}")
            raise CartOperationError(f"Failed to get cart items: {str(e)}") from e

    def clear_cart(self):
        """Clear database cart"""
        try:
            Cart.objects.filter(user=self._user).delete()
            logger.info("Cart cleared successfully")
            return {
                'success': True,
                'message': 'Cart deleted',
                'cart_count': 0,
            }
        except Exception as e:
            logger.error(e)
            raise CartOperationError(f"Failed to clear cart: {str(e)}") from e

    def save_cart(self):
        try:
            cart = Cart.objects.filter(user=self._user)
            for item in cart:
                item.save()
            logger.info("Cart saved to database")
            return {
                'success': True,
                'message': 'Cart saved',
            }
        except Exception as e:
            logger.error(f'Cart not saved to database: {str(e)}')
            raise CartOperationError(f"Failed to save cart: {str(e)}") from e

    def bulk_update_items(self, cart_items):
        """Bulk update cart items quantities"""
        try:
            Cart.objects.bulk_update(cart_items, ['quantity'])
            logger.info(f"Bulk updated {len(cart_items)} cart items")
        except Exception as e:
            logger.error(f"Error bulk updating cart items: {str(e)}")
            raise CartOperationError(f"Failed to bulk update cart items: {str(e)}") from e

    def bulk_create_items(self, cart_items):
        """Bulk create new cart items"""
        try:
            Cart.objects.bulk_create(cart_items)
            logger.info(f"Bulk created {len(cart_items)} cart items")
        except Exception as e:
            logger.error(f"Error bulk creating cart items: {str(e)}")
            raise CartOperationError(f"Failed to bulk create cart items: {str(e)}") from e


class CartSyncService:
    """Service for synchronizing carts between session and database"""

    @staticmethod
    def sync_session_to_db(request):
        """
        Synchronize cart items from session to database after user login.
        Transfers all items from CartSession to CartDB and clears the session cart.
        """
        from myapp.models import Product

        # Get session cart
        session_cart = CartSession(request)
        session_data = session_cart._cart

        if not session_data:
            logger.info("No items in session cart to sync")
            return

        # Get all product IDs from session
        product_ids = [int(pid) for pid in session_data.keys()]

        # ONE query to fetch all products
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {product.id: product for product in products}

        # ONE query to fetch all existing cart items for this user
        existing_cart_items = Cart.objects.filter(
            user=request.user,
            product_id__in=product_ids
        ).select_related('product')
        existing_cart_dict = {item.product_id: item for item in existing_cart_items}

        # Prepare cart items for bulk operations
        cart_items_to_update = []
        cart_items_to_create = []

        for product_id_str, item_data in session_data.items():
            product_id = int(product_id_str)
            product = products_dict.get(product_id)

            if not product:
                logger.warning(f"Product {product_id} not found, skipping sync")
                continue

            quantity = item_data.get('quantity', 1)

            # Check if item already exists in DB cart
            existing_item = existing_cart_dict.get(product_id)
            if existing_item:
                # Update existing item
                existing_item.quantity += quantity
                cart_items_to_update.append(existing_item)
            else:
                # Create new item
                cart_items_to_create.append(
                    Cart(user=request.user, product=product, quantity=quantity)
                )

        # Use CartDB methods for bulk operations
        db_cart = CartDB(request)
        
        if cart_items_to_update:
            db_cart.bulk_update_items(cart_items_to_update)

        if cart_items_to_create:
            db_cart.bulk_create_items(cart_items_to_create)

        synced_count = len(cart_items_to_update) + len(cart_items_to_create)

        # Clear session cart after successful sync
        if synced_count > 0:
            session_cart.clear_cart()
            logger.info(f"Successfully synced {synced_count} items from session to DB cart")


class CartSession(CartInterface, CartCalculatorMixin):
    def __init__(self, request: HttpRequest) -> None:
        self._request = request
        self._session = request.session
        self._cart = self._session.get('cart', {})
        self._user = request.user

    def add_to_cart(self, product: Product):
        try:
            """Add product to session cart"""
            product_id_str = str(product.id)

            if product_id_str in self._cart:
                self._cart[product_id_str]['quantity'] += 1
            else:
                self._cart[product_id_str] = {
                    'quantity': 1,
                    'price': str(product.price),
                    'name': product.name,
                    'image': product.image.url if product.image else ''
                }

            self.save_cart()
            return {
                'success': True,
                'message': 'Product added to cart',
                'cart_count': self.get_cart_count(),
                'in_db': False
            }
        except Exception as e:
            logger.error(f"Error adding product to cart: {str(e)}")
            raise CartOperationError(f"Failed to add product to session cart: {str(e)}") from e

    def update_quantity(self, product_id: int, quantity_change: int):
        """Update product quantity"""
        product_id_str = str(product_id)

        if product_id_str in self._cart:
            new_quantity = self._cart[product_id_str]['quantity'] + quantity_change

            if new_quantity <= 0:
                del self._cart[product_id_str]
                item_quantity = 0
            else:
                self._cart[product_id_str]['quantity'] = new_quantity
                item_quantity = new_quantity

            self.save_cart()

            return {
                'success': True,
                'message': 'Quantity updated',
                'cart_count': self.get_cart_count(),
                'item_quantity': item_quantity
            }

        return {
            'success': False,
            'message': 'Product not found in cart'
        }

    def remove_from_cart(self, product_id: int):
        product_id_str = str(product_id)

        if product_id_str in self._cart:
            del self._cart[product_id_str]
            self.save_cart()

            return {
                'success': True,
                'message': 'Product removed from cart',
                'cart_count': self.get_cart_count(),
            }

        return {
            'success': False,
            'message': 'Product not found in cart',
            'cart_count': self.get_cart_count(),
        }

    def get_cart_count(self):
        """Calculate total items count"""
        return sum(item['quantity'] for item in self._cart.values())

    def get_cart_items(self):
        """Get cart items for template from session"""
        from decimal import Decimal
        from myapp.models import Product

        try:
            cart = self._request.session.get('cart', {})
            cart_items = []
            products_to_remove = []

            product_ids = [int(pid) for pid in cart.keys()]
            
            products = Product.objects.filter(id__in=product_ids)
            products_dict = {product.id: product for product in products}

            for product_id_str, item in cart.items():
                product_id = int(product_id_str)
                product = products_dict.get(product_id)
                
                if product is None:
                    products_to_remove.append(product_id_str)
                    continue

                cart_items.append(
                    self._build_cart_item(
                        product=product,
                        quantity=item['quantity'],
                        price=item['price']
                    )
                )

            if products_to_remove:
                for product_id in products_to_remove:
                    del cart[product_id]
                self.save_cart()

            total_price = self._calculate_total_price(cart_items)

            return {
                'cart_items': cart_items,
                'total_price': total_price,
                'cart_count': self.get_cart_count(),
                'in_db': False
            }

        except Exception as e:
            logger.error(f"Error getting cart data from session: {str(e)}")
            raise CartOperationError(f"Failed to get cart items from session: {str(e)}") from e

    def save_cart(self):
        """Save cart to session"""
        try:
            self._request.session['cart'] = self._cart
            self._request.session.modified = True
            logger.info('Cart saved to session')
            return {
                'success': True,
                'message': 'Cart saved to session',
            }
        except Exception as e:
            logger.error(f'Cart not saved to session: {str(e)}')
            raise CartOperationError(f"Failed to save cart to session: {str(e)}") from e

    def clear_cart(self):
        """Clear entire cart"""
        self._request.session['cart'] = {}
        self._request.session.modified = True
        return {
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0,
        }
