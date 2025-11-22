from django import forms
from django.core.validators import MinLengthValidator, RegexValidator

from .models import Order
from .constants import (
    ADDRESS_REGEX, CITY_REGEX,
    ADDRESS_MIN_LENGTH_MESSAGE, ADDRESS_INVALID_CHARS_MESSAGE,
    CITY_MIN_LENGTH_MESSAGE, CITY_INVALID_CHARS_MESSAGE,
    ADDRESS_MIN_LENGTH, ADDRESS_MAX_LENGTH,
    CITY_MIN_LENGTH, CITY_MAX_LENGTH
)


class OrderCreateForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[
            MinLengthValidator(ADDRESS_MIN_LENGTH, message=ADDRESS_MIN_LENGTH_MESSAGE),
            RegexValidator(regex=ADDRESS_REGEX, message=ADDRESS_INVALID_CHARS_MESSAGE)
        ],
        max_length=ADDRESS_MAX_LENGTH,
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[
            MinLengthValidator(CITY_MIN_LENGTH, message=CITY_MIN_LENGTH_MESSAGE),
            RegexValidator(regex=CITY_REGEX, message=CITY_INVALID_CHARS_MESSAGE)
        ],
        max_length=CITY_MAX_LENGTH,
    )
    class Meta:
        model = Order
        fields = ['address', 'city']

        labels = {
            'address': 'Address',
            'city': 'City',
        }

        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
        }
