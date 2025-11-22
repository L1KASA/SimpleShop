from favorites.services import FavoriteService

def favorites_count(request):
    """Context processor to add favorites count to all templates"""
    count = FavoriteService.get_favorites_count(request)
    return {'favorites_count': count}
