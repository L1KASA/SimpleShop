from django.shortcuts import render, get_object_or_404
from category.models import Category
from myapp.models import Product
from myapp.services import CoreService


def index(request):

    filter_params = CoreService.extract_filter_params(request)

    items = CoreService.get_filtred_products(filter_params)
    
    from favorites.services import FavoriteService
    favorites_ids = FavoriteService.get_favorites_ids(request)

    context = {
        'items': items,
        'categories': Category.objects.all(),
        'favorites_ids': favorites_ids,
    }
    return render(request, "index.html", context)


def id_item(request, id):
    item = get_object_or_404(Product, pk=id)
    
    from favorites.services import FavoriteService
    is_favorite = FavoriteService.is_favorite(request, id)
    
    return render(request, "phone.html", {'item': item, 'is_favorite': is_favorite})
