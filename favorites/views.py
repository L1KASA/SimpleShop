from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from djangoProject.decorators import handler_api_errors
from favorites.services import FavoriteService


@handler_api_errors
@require_POST
def favorite_toggle(request, product_id):
    result = FavoriteService.toggle_favorite(request, product_id)
    return JsonResponse(result)


@handler_api_errors
def favorites_list(request):
    favorites_data = FavoriteService.get_favorites(request)

    context = {
        'products': favorites_data['products'],
        'favorites_count': favorites_data['favorites_count'],
    }

    return render(request, 'favorites/list.html', context)
