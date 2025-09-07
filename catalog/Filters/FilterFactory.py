from categories.Filters.Filters import MinPriceFilter, MaxPriceFilter, CategoryFilter, MinWeightFilter, MaxWeightFilter


class FilterFactory:
    def __init__(self):
        self.filters = {
            'min_price': MinPriceFilter,
            'max_price': MaxPriceFilter,
            'categories': CategoryFilter,
            'min_weight': MinWeightFilter,
            'max_weight': MaxWeightFilter,
        }

    def create_filters(self, filters_params):
        filter_list = []

        for key, value in filters_params.items():
            if key in self.filters and value is not None:
                filter_list.append(self.filters[key](value))

        return filter_list
