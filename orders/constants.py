"""
Constants for order validation
"""

# Validation patterns
ADDRESS_REGEX = r'^[a-zA-Zа-яА-Я0-9\s\.,-]+$'
CITY_REGEX = r'^[a-zA-Zа-яА-Я\s-]+$'

# Validation messages
ADDRESS_MIN_LENGTH_MESSAGE = "Адрес должен содержать минимум 5 символов"
ADDRESS_INVALID_CHARS_MESSAGE = "Адрес содержит недопустимые символы"
CITY_MIN_LENGTH_MESSAGE = "Название города должно содержать минимум 2 символа"
CITY_INVALID_CHARS_MESSAGE = "Название города содержит недопустимые символы"

# Field constraints
ADDRESS_MIN_LENGTH = 5
ADDRESS_MAX_LENGTH = 200
CITY_MIN_LENGTH = 2
CITY_MAX_LENGTH = 100
