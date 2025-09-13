from django.http import HttpRequest

from cart.CartBase import CartDB, CartSession, CartInterface


class CartFactory:
    @staticmethod
    def build_cart(request: HttpRequest) -> CartInterface:
        """Builds cart db"""
        if request.user.is_authenticated:
            return CartDB(request)
        else:
            return CartSession(request)
