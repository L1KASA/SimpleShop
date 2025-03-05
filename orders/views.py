import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

logger = logging.getLogger(__name__)

# orders/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from cart.Cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem
from myapp.models import Product

def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        # Извлекаем выбранные товары из сессии
        selected_ids = request.session.get('selected_products', [])
        logger.warning(f"POST selected_ids: {selected_ids}")  # Логируем список ID

        # Обработка формы заказа
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            # Добавляем товары в заказ
            for product_id in selected_ids:
                product_id_str = str(product_id)
                cart_item = cart.cart.get(product_id_str)
                if not cart_item:
                    logger.warning(f"Товар {product_id} не найден в корзине")
                    continue
                product_id_int = int(product_id)
                product = get_object_or_404(Product, id=product_id_int)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=cart_item['price'],
                    quantity=cart_item['quantity']
                )

            # Удаляем выбранные товары из корзины
            for pid in selected_ids:
                pid_str = str(pid)
                if pid_str in cart.cart:
                    del cart.cart[pid_str]
            cart.save()

            # Очищаем сессию от выбранных товаров
            if 'selected_products' in request.session:
                del request.session['selected_products']

            return redirect('orders:order_created', order_id=order.id)
    else:
        # Для GET-запроса берем выбранные товары из запроса и сохраняем в сессию
        selected_ids = json.loads(request.GET.get('selected_products', '[]'))
        request.session['selected_products'] = selected_ids  # Сохраняем в сессию
        logger.warning(f"GET selected_ids: {selected_ids}")  # Логируем список ID
        form = OrderCreateForm()

    # Формируем данные для отображения выбранных товаров
    selected_items = {str(pid): cart.cart[str(pid)] for pid in selected_ids if str(pid) in cart.cart}
    total_price = sum(
        float(item['price']) * item['quantity']
        for item in selected_items.values()
    )

    return render(request, 'orders/order/create.html', {
        'form': form,
        'selected_items': selected_items,
        'total_price': total_price,
    })

def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    order_items = order.items.all()

    return render(
        request,
        'orders/order/created.html',
        {'order': order, 'total_price': order.get_total_price(),
         'order_items': order_items}
    )
def order_info(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')

    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'orders/profile/info.html', {'page_obj': page_obj})