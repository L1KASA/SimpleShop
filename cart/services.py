from django.shortcuts import get_object_or_404
from categories.models import Product
from decimal import Decimal


class CartService:

    @staticmethod
    def get_cart(request):
        """Get cart from session"""
        return request.session.get('cart', {})

    @staticmethod
    def save_cart(request, cart):
        """Save cart to session"""
        request.session['cart'] = cart
        request.session.modified = True

    @staticmethod
    def add_to_cart(request, product_id):
        """Add product to cart"""
        cart = CartService.get_cart(request)
        product = get_object_or_404(Product, id=product_id)
        product_id_str = str(product_id)

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {
                'quantity': 1,
                'price': str(product.price),
                'name': product.name,
                'image': product.image.url if product.image else ''
            }

        CartService.save_cart(request, cart)

        return {
            'success': True,
            'message': 'Product added to cart',
            'cart_count': CartService.get_cart_total(cart)
        }

    @staticmethod
    def remove_from_cart(request, product_id):
        """Remove product from cart"""
        cart = CartService.get_cart(request)
        product_id_str = str(product_id)

        if product_id_str in cart:
            del cart[product_id_str]
            CartService.save_cart(request, cart)

            return {
                'success': True,
                'message': 'Product removed from cart',
                'cart_count': CartService.get_cart_total(cart)
            }

        return {
            'success': False,
            'message': 'Product not found in cart'
        }

    @staticmethod
    def update_quantity(request, product_id, quantity_change):
        """Update product quantity"""
        cart = CartService.get_cart(request)
        product_id_str = str(product_id)

        if product_id_str in cart:
            new_quantity = cart[product_id_str]['quantity'] + quantity_change

            if new_quantity <= 0:
                del cart[product_id_str]
                item_quantity = 0
            else:
                cart[product_id_str]['quantity'] = new_quantity
                item_quantity = new_quantity

            CartService.save_cart(request, cart)

            return {
                'success': True,
                'message': 'Quantity updated',
                'cart_count': CartService.get_cart_total(cart),
                'item_quantity': item_quantity
            }

        return {
            'success': False,
            'message': 'Product not found in cart'
        }

    @staticmethod
    def get_cart_data(request):
        """Get cart data for template"""
        cart = CartService.get_cart(request)
        cart_items = []
        total_price = Decimal('0.00')

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
                # Удаляем несуществующий товар
                del cart[product_id]
                CartService.save_cart(request, cart)

        return {
            'cart_items': cart_items,
            'total_price': total_price,
            'cart_count': CartService.get_cart_total(cart)
        }

    @staticmethod
    def get_cart_total(cart):
        """Calculate total items count"""
        return sum(item['quantity'] for item in cart.values())

    @staticmethod
    def clear_cart(request):
        """Clear entire cart"""
        request.session['cart'] = {}
        request.session.modified = True
        return True