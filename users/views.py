from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from djangoProject import settings
from .forms import NewUserForm, LoginUserForm, UserPasswordChangeForm, ProfileUserForm, CustomPasswordResetConfirmForm
from .forms import CustomPasswordResetForm
from django.contrib.auth.views import PasswordResetView, \
    PasswordResetConfirmView


class RegisterUser(CreateView):
    """Handles user registration."""
    form_class = NewUserForm
    template_name = 'users/signup.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        if self.request.recaptcha_is_valid:
            form.save()
            return super().form_valid(form)

        return render(self.request, 'users/signup.html', self.get_context_data())


class LoginUser(LoginView):
    """Handles user login."""
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход'}

    def post(self, request, *args, **kwargs):
        if not request.recaptcha_is_valid:
            return self.form_invalid(self.get_form())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Called after successful login - sync session cart to DB"""
        response = super().form_valid(form)
        
        # Sync session cart to database cart
        from cart.CartBase import CartSyncService
        CartSyncService.sync_session_to_db(self.request)
        
        return response

    def get_success_url(self):
        return reverse('myapp:index')


class ProfileUser(LoginRequiredMixin, UpdateView):
    """Handles user profile updates."""
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {
        'title': 'Профиль пользователя',
        'default_image': settings.DEFAULT_USER_IMAGE,
    }

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'profile'
        context['edit_mode'] = self.request.GET.get('edit', 'false') == 'true'
        return context


class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    """Handles user password change."""
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_complete')
    template_name = "users/password_change.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'change_password'
        return context

    def post(self, request, *args, **kwargs):
        if not request.recaptcha_is_valid:
            return self.form_invalid(self.get_form())
        return super().post(request, *args, **kwargs)


def delete_user(request):
    """Handles user deletion."""
    if request.method == 'POST':
        user = request.user
        user.delete()

        return redirect('users:delete_user')

    return render(request, 'delete_user_completed.html')


class CustomPasswordResetView(PasswordResetView):
    """Handles user password reset functionality."""
    form_class = CustomPasswordResetForm
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:users/password_reset_done")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Handles user password reset confirmation."""
    form_class = CustomPasswordResetConfirmForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")
