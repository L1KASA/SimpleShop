
from django.urls import path

from . import views
from .views import cart_view

app_name = 'cart'
urlpatterns = [
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),

    path('', cart_view, name='cart_view'),

    path('update/', views.cart_update, name='cart_update'),

    path('delete/', views.cart_delete, name='cart_delete'),

    #path('count/', views.cart_count, name='cart_count'),


]
