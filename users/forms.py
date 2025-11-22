import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django import forms
from django.contrib.auth.forms import PasswordResetForm


class NewUserForm(UserCreationForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(required=True, label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(required=True, label='Повторите пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }
        error_messages = {
            'email': {
                'unique': "Такой E-mail уже существует!",
            },
        }

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин/E-mail',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля",
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    this_year = datetime.date.today().year
    date_birth = forms.DateField(label='Дата рождения',
                                 widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))

    class Meta:
        model = get_user_model()
        fields = ['photo', 'first_name', 'last_name', 'username', 'email', 'date_birth']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'E-mail',
            'username': 'Логин',
            'date_birth': 'Дата рождения',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )

class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля",
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))
