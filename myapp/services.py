from myapp.Filters.FilterFactory import FilterFactory
from myapp.models import Product


class CoreService:
    @staticmethod
    def extract_filter_params(request):
        converters = {
            'min_price': int,
            'max_price': int,
            'category': str,
            'min_weight': float,
            'max_weight': float,
        }

        filter_params = {}

        for key, converter in converters.items():
            value = request.GET.get(key)
            filter_params[key] = CoreService._convert_param(value, converter)

        return filter_params

    @staticmethod
    def _convert_param(value, converter):
        return converter(value) if value else None

    @staticmethod
    def get_filtred_products(filter_params):
        filters = FilterFactory().create_filters(filter_params)

        items = Product.objects.all()

        for filter_instance in filters:
            items = filter_instance.apply_filter(items)
        return items
