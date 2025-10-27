from django import forms
from django.core.validators import MinLengthValidator, RegexValidator

from .models import Order


class OrderCreateForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[
            MinLengthValidator(
                5, message="Адрес должен содержать минимум 5 символов"
            ),
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-Я0-9\s\.,-]+$',
                message="Адрес содержит недопустимые символы"
            )
        ],
        max_length=200,
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        validators=[
            MinLengthValidator(
                2, message='Название города должно содержать минимум 2 символа'
            ),
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-Я\s-]+$',
                message='Название города содержит недопустимые символы'
            )
        ],
        max_length=100,
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
