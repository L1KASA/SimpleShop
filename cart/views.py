from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST
from cart.services import CartService
from django.http import JsonResponse
from djangoProject.decorators import handler_api_errors
from djangoProject.utils import parse_json_body


@handler_api_errors
@require_POST
def cart_add(request, product_id):
    """Handle adding product to cart"""
    result = CartService.add_to_cart(request, product_id)
    return JsonResponse(result)


@handler_api_errors
def cart_view(request):
    """Handle cart view"""
    cart_data = CartService.get_cart_items(request)


    context = {
        'cart_items': cart_data['cart_items'],
        'total_price': cart_data['total_price'],
        'cart_count': cart_data['cart_count']
    }

    return render(request, 'cart/cart-view.html', context)


@login_required
@handler_api_errors
@require_POST
def cart_delete(request):
    """Handle remove product from cart"""
    data = parse_json_body(request)
    product_id = int(data.get('product_id'))

    result = CartService.remove_from_cart(request, product_id)
    return JsonResponse(result)


@login_required
@handler_api_errors
@require_POST
def cart_update(request):
    """Handle updating product quantity in cart"""
    data = parse_json_body(request)
    product_id = str(data.get('product_id'))
    quantity_change = int(data.get('quantity_change'))

    result = CartService.update_quantity(request, product_id, quantity_change)
    return JsonResponse(result)
