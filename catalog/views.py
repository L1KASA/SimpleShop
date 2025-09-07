from django.shortcuts import render, get_object_or_404
from categories.models import Category
from catalog.models import Product
from catalog.services import CoreService


def index(request):

    filter_params = CoreService.extract_filter_params(request)

    items = CoreService.get_filtred_products(filter_params)

    context = {
        'items': items,
        'categories': Category.objects.all()
    }
    return render(request, "index.html", context)


def catalog_detail(request, id):
    item = get_object_or_404(Product, pk=id)
    return render(request, "phone.html", {'item': item})
