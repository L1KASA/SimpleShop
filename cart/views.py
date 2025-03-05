from django.shortcuts import render, get_object_or_404

from cart.Cart import Cart
from cart.models import Cart as CartModel
from myapp.models import Product


def cart_add(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    pr = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)

    if request.method == 'POST':
        cart.add(pr)

        # Получаем товары, которые были добавлены в корзину и выбраны для заказа
        selected_product_ids = json.loads(
            request.POST.get('selected_products', '[]'))  # Получаем только выбранные товары

        if product_id in selected_product_ids:  # Проверяем, был ли этот товар выбран для добавления в заказ
            if request.user.is_authenticated:
                # Получаем или создаем запись в базе данных о товаре в корзине пользователя
                cart_item, created = CartModel.objects.get_or_create(user=request.user, product=pr)
                if not created:
                    cart_item.quantity = cart.cart.get(str(pr.id), {}).get('quantity', 0)
                else:
                    cart_item.quantity += 1
                cart_item.save()

        total_cart_count = cart.__len__()

        return JsonResponse({'cart_count': total_cart_count})


def cart_view(request):
    cart = Cart(request)
    selected_ids = request.session.get('selected_products', [])
    selected_products_json = json.dumps(selected_ids)
    total_price = cart.get_total_price()

    total_count = cart.__len__()

    return render(request, 'cart/cart-view.html',
                  {
                      'cart': cart,
                      'total_price': total_price,
                      'cart_count': total_count,
                      'selected_products_json': selected_products_json,
                  })


def cart_delete(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = Cart(request)
        product_id = int(data.get('product_id'))

        cart.delete(product_id)

        CartModel.objects.filter(user=request.user, product=product_id).delete()

        quantity = cart.__len__()

        total_price = cart.get_total_price()

        return JsonResponse({'cart_count': quantity, 'total_price': total_price})


import json

from django.http import JsonResponse


def cart_update(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        cart = Cart(request)
        product_id = str(data.get('product_id'))
        quantity_change = int(data.get('quantity_change'))

        if product_id not in cart.cart:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        cart.update(product_id, quantity_change)

        updated_quantity = cart.cart.get(product_id, {}).get('quantity', 0)

        total_count = cart.__len__()

        return JsonResponse({
            'updated_quantity': updated_quantity,
            'cart_count': total_count,
            'total_price': cart.get_total_price()
        })


def cart_count(request):
    cart = Cart(request)
    count = cart.get_total_count()  # Метод, возвращающий количество товаров
    return JsonResponse({'cart_count': count})