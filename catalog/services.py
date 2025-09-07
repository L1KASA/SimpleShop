from categories.Filters.FilterFactory import FilterFactory
from categories.models import Product


class CoreService:
    @staticmethod
    def extract_filter_params(request):
        converters = {
            'min_price': int,
            'max_price': int,
            'categories': str,
            'min_weight': float,
            'max_weight': float,
        }

        filter_params = {}

        # Проходим по всем параметрам и их конвертерам
        for key, converter in converters.items():
            # Получаем значение параметра из запроса
            value = request.GET.get(key)
            # Конвертируем значение и добавляем в словарь
            filter_params[key] = CoreService._convert_param(value, converter)

        return filter_params

    def _convert_param(value, converter):
        return converter(value) if value else None

    @staticmethod
    def get_filtred_products(filter_params):
        filters = FilterFactory().create_filters(filter_params)

        # QuerySet всех продуктов
        items = Product.objects.all()

        # Применяем фильтры
        for filter_instance in filters:
            items = filter_instance.apply_filter(items)
        return items
