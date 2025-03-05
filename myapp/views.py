from django.http import Http404
from django.shortcuts import render

from category.models import Category
from myapp.Filters.FilterFactory import FilterFactory
from myapp.exceptioins import ProductNotFoundException
from myapp.models import Product


def index(request):
    # Получаем параметры фильтров и конвертируем их в нужные типы
    filter_params = {
        'min_price': int(request.GET.get('min_price')) if request.GET.get('min_price') else None,
        'max_price': int(request.GET.get('max_price')) if request.GET.get('max_price') else None,
        'category': request.GET.get('category') if request.GET.get('category') else None,
        'min_weight': float(request.GET.get('min_weight')) if request.GET.get('min_weight') else None,
        'max_weight': float(request.GET.get('max_weight')) if request.GET.get('max_weight') else None,
    }

    factory = FilterFactory()
    filters = factory.create_filters(filter_params)

    # QuerySet всех продуктов
    items = Product.objects.all()

    # Применяем фильтры*
    for filter_instance in filters:
        items = filter_instance.apply_filter(items)
    categories = Category.objects.all()
    context = {'items': items, 'categories': categories}
    return render(request, "index.html", context)


def id_item(request, id):
    try:
        item = Product.objects.get(id=id)
    except ProductNotFoundException as e:
        raise Http404(str(e))
    context = {'item': item}
    return render(request, "phone.html", context)



