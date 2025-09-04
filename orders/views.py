import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from djangoProject.decorators import handler_api_errors
from .services import OrderViewService


from django.shortcuts import render, redirect, get_object_or_404
from .models import Order


logger = logging.getLogger(__name__)


@login_required
@handler_api_errors
def order_create(request):
    """Handles creating a new order."""
    order, context = OrderViewService.prepare_order_create_context(request)
    if order:
        return redirect('orders:order_created', order_id=order.id)
    return render(request, 'orders/order/create.html', context)


@login_required
@handler_api_errors
def order_created(request, order_id):
    """Displays the details of a successefully created order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    order_items = order.items.all()

    return render(
        request,
        'orders/order/created.html',
        {
            'order': order,
            'total_price': order.get_total_price(),
            'order_items': order_items
        }
    )


@login_required
@handler_api_errors
def order_info(request):
    """Displays a paginated list of orders for the logged-in user."""
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
