from .services import CartService

def cart_context(request):
    """Добавляет данные корзины в контекст всех шаблонов"""
    cart_data = CartService.get_cart_items(request)
    return {
        'cart_count': cart_data['cart_count'],
        'cart_total_price': cart_data['total_price']
    }