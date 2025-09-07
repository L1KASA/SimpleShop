
from django.urls import path

from catalog.views import index, catalog_detail

app_name = 'catalog'
urlpatterns = [
    path('catalog/', index, name='index'),

    path('catalog/<int:id>/', catalog_detail, name='catalog_detail'),

]
