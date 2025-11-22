import json
import logging
from decimal import Decimal

from cart.CartFactory import CartFactory
from orders.forms import OrderCreateForm
from orders.models import OrderItem

logger = logging.getLogger(__name__)


class OrderService:
    """Service class for handling order operations."""

    @staticmethod
    def create_order(user, form, cart_handler, selected_ids):
        """
        Creates an order for the user based on the selected items in the cart.
        :param user: The user placing the order.
        :param form: The order creation form.
        :param cart_handler: The cart handler (CartDB or CartSession).
        :param selected_ids: List of the selected product ids.
        :return: The created order if successful, None otherwise.
        """
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.save()

            cart_data = cart_handler.get_cart_items()
            cart_items = {str(item['product'].id): item for item in cart_data['cart_items']}

            order_items = []
            for product_id in selected_ids:
                product_id_str = str(product_id)
                if product_id_str not in cart_items:
                    logger.warning(f"Product {product_id} not found in cart for user {user.id}")
                    continue

                cart_item = cart_items[product_id_str]
                product = cart_item['product']

                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        price=cart_item['price'],
                        quantity=cart_item['quantity']
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            for product_id in selected_ids:
                cart_handler.remove_from_cart(product_id)

            return order
        return None


class OrderViewService:
    """Service class for preparing context and handling order view logic."""

    @staticmethod
    def prepare_order_create_context(request):
        """
        Prepares context for order creation page.
        :param request: The HTTP request object.
        :return: A tuple containing with order (if created) and the context dictionary.
        """
        cart_handler = CartFactory.build_cart(request)
        selected_ids = request.session.get('selected_products', [])

        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            order = OrderService.create_order(request.user, form, cart_handler, selected_ids)
            if order:
                OrderViewService._clear_selected_products_from_session(request)
                return order, None  # Возвращаем заказ и пустой контекст для редиректа
        else:
            selected_ids = json.loads(request.GET.get('selected_products', '[]'))
            request.session['selected_products'] = selected_ids
            logger.warning(f"GET selected_ids: {selected_ids}")
            form = OrderCreateForm()

        selected_items = OrderViewService._get_selected_items(cart_handler, selected_ids)
        total_price = OrderViewService._calculate_total_price(selected_items)

        return None, {
            'form': form,
            'selected_items': selected_items,
            'total_price': total_price,
        }

    @staticmethod
    def _clear_selected_products_from_session(request):
        """
        Clears selected products from the session.
        :param request: The HTTP request object.
        """
        if 'selected_products' in request.session:
            del request.session['selected_products']

    @staticmethod
    def _get_selected_items(cart_handler, selected_ids):
        """
        Retrieves selected items from the cart.
        :param cart_handler: The cart handler instance.
        :param selected_ids: List of selected products ids.
        :return: A dictionary of selected items.
        """
        cart_data = cart_handler.get_cart_items()
        cart_items = {str(item['product'].id): item for item in cart_data['cart_items']}

        selected_items = {}
        for pid in selected_ids:
            pid_str = str(pid)
            if pid_str in cart_items:
                cart_item = cart_items[pid_str]
                selected_items[pid_str] = {
                    'product_name': cart_item['product'].name,
                    'price': cart_item['price'],
                    'quantity': cart_item['quantity'],
                }
        return selected_items

    @staticmethod
    def _calculate_total_price(selected_items):
        """
        Calculates the total price for selected items.
        :param selected_items: Dictionary of selected items.
        :return: Total price as Decimal.
        """
        return sum(
            Decimal(str(item['price'])) * item['quantity']
            for item in selected_items.values()
        )
