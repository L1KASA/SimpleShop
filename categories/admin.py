from django.contrib import admin

from categories.models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')  # Отображаемые поля в списке категорий
    search_fields = ('name',)  # Поля, по которым можно искать
    list_filter = ('name',)  # Возможность фильтровать по полям
    ordering = ('id',)  # Сортировка по ID
