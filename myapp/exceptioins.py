class ProductNotFoundException(Exception):
    """
    Исключение для случая, если продукт не найден в базе данных.
    """
    def __init__(self, message="Product not found"):
        super().__init__(message)