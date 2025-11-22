from django.urls import path

from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle/<int:product_id>/', views.favorite_toggle, name='toggle'),
    path('', views.favorites_list, name='list'),
]
