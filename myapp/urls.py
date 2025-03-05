
from django.urls import path

from category import views
from myapp.views import index, id_item

app_name = 'myapp'
urlpatterns = [
    path('myapp/', index, name='index'),

    path('myapp/<int:id>/', id_item, name='id_item'),

]
