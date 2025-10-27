from abc import ABC, abstractmethod

class FilterInterface(ABC):
    """
    Интерфейс для фильтров
    """

    @abstractmethod
    def apply_filter(self, queryset):
        """
        Применяет фильтр QuerySet.
        :param queryset: QuerySet для фильтрации.
        :return: Отфильтрованный QuerySet.
        """
        pass


class MinPriceFilter(FilterInterface):
    def __init__(self, min_price):
        self.min_price = min_price

    def apply_filter(self, queryset):
        """
        Фильтрует QuerySet по минимальной цене.
        """
        if self.min_price:
            return queryset.filter(price__gte=self.min_price)
        return queryset


class MaxPriceFilter(FilterInterface):
    def __init__(self, max_price):
        self.max_price = max_price

    def apply_filter(self, queryset):
        """
        Фильтрует QuerySet по максимальной цене.
        """
        if self.max_price:
            return queryset.filter(price__lte=self.max_price)
        return queryset


class CategoryFilter(FilterInterface):
    def __init__(self, category):
        self.category = category

    def apply_filter(self, queryset):
        """
        Фильтрует QuerySet по категории.
        """
        if self.category:
            return queryset.filter(category__name=self.category)
        return queryset

class MinWeightFilter(FilterInterface):
    def __init__(self, min_weight):
        self.min_weight = min_weight

    def apply_filter(self, queryset):
        """
        Фильтрует QuerySet по минимальному весу.
        """
        if self.min_weight:
            return queryset.filter(weight__gte=self.min_weight)
        return queryset

class MaxWeightFilter(FilterInterface):
    def __init__(self, max_weight):
        self.max_weight = max_weight

    def apply_filter(self, queryset):
        """
        Фильтрует QuerySet по максимальному весу.
        """
        if self.max_weight:
            return queryset.filter(weight__lte=self.max_weight)
        return queryset
