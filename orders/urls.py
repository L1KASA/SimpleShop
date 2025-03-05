from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.template.defaulttags import url
from django.urls import path, reverse_lazy

from . import views



app_name = 'orders'
urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('created/<int:order_id>/', views.order_created, name='order_created'),
    path('info/', views.order_info, name='order_info'),
]

