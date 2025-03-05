from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
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
