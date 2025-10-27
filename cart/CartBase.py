import logging
from abc import abstractmethod, ABC

from django.db.models import Sum
from django.http import HttpRequest
from typing import Any, Dict

from cart.models import Cart
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


class CartDB(CartInterface):
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
            return {
                'success': False,
                'message': 'Error adding product to cart',
                'cart_count': self.get_cart_count(),
                'in_db': True,
            }

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
            return {
                'success': False,
                'message': 'Product not found in cart',
                'cart_count': self.get_cart_count(),
            }

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
        try:
            cart = Cart.objects.filter(user=self._user).select_related('product')
            cart_items = []
            total_price = Decimal('0.00')

            for cart_item in cart:
                item_total = cart_item.product.price * cart_item.quantity
                total_price += item_total

                cart_items.append({
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'total_price': item_total,
                    'price': cart_item.product.price,
                    'image': cart_item.product.image.url if cart_item.product.image else '',
                    'name': cart_item.product.name
                })
            return {
                'cart_items': cart_items,
                'total_price': total_price,
                'cart_count': self.get_cart_count(),
                'in_db': True
            }

        except Exception as e:
            logger.error(f"Error getting cart data from DB: {str(e)}")
            return {
                'cart_items': [],
                'total_price': Decimal('0.00'),
                'cart_count': 0,
                'in_db': True,
                'error': str(e)
            }

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
            return {
                'success': False,
                'message': 'Cart not deleted',
            }

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
            return {
                'success': False,
                'message': 'Cart not saved',
            }


class CartSession(CartInterface):
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
            logger.error(f"Database error adding product to cart: {str(e)}")
            raise

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
            total_price = Decimal('0.00')
            products_to_remove = []

            for product_id, item in cart.items():
                try:
                    product = Product.objects.get(id=int(product_id))
                    item_total = Decimal(item['price']) * item['quantity']
                    total_price += item_total

                    cart_items.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'total_price': item_total,
                        'price': Decimal(item['price']),
                        'image': item.get('image', ''),
                        'name': item.get('name', '')
                    })
                except Product.DoesNotExist:
                    # Помечаем несуществующий товар для удаления
                    products_to_remove.append(product_id)

            # Удаляем несуществующие товары
            if products_to_remove:
                for product_id in products_to_remove:
                    del cart[product_id]
                self.save_cart()

            return {
                'cart_items': cart_items,
                'total_price': total_price,
                'cart_count': self.get_cart_count(),
                'in_db': False
            }

        except Exception as e:
            logger.error(f"Error getting cart data from session: {str(e)}")
            return {
                'cart_items': [],
                'total_price': Decimal('0.00'),
                'cart_count': 0,
                'in_db': False,
                'error': str(e)
            }

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
            return {
                'success': False,
                'message': 'Cart not saved to session',
            }

    def clear_cart(self):
        """Clear entire cart"""
        self._request.session['cart'] = {}
        self._request.session.modified = True
        return {
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0,
        }
