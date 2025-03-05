from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy

from . import views
from .decorators import check_recaptcha
from .views import ProfileUser, delete_user, CustomPasswordResetView, CustomPasswordResetConfirmView

app_name = 'users'
urlpatterns = [
    path('signup/', check_recaptcha(views.RegisterUser.as_view()), name='signup'),
    path('login/', check_recaptcha(views.LoginUser.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('change-password/', check_recaptcha(views.UserPasswordChange.as_view()), name='change_password'),
    #path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/complete/', PasswordChangeDoneView.as_view(template_name="users/password_change_complete.html"), name='password_change_complete'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='users/password_reset_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name='password_reset_complete'),
    path('delete-user/', delete_user, name='delete_user'),

]

