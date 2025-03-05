from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


def new_users_handler(backend, user, response, *args, **kwargs):
    try:
        # Пытаемся найти пользователя по email
        user = get_user_model().objects.get(email=user.email)
    except get_user_model().DoesNotExist:
        # Если пользователя с таким email нет, создаем нового
        user = get_user_model().objects.create(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # Добавляем пользователя в группу 'social', если она существует
        group = Group.objects.filter(name='social').first()
        if group:
            user.groups.add(group)

    # Обработка social_user
    social_user = user.social_auth.filter(provider=backend.name).first()

    if social_user is None:
        # Здесь можно логировать ошибку или сделать дополнительные действия
        raise ValueError("Social user is None. Cannot find the provider for this user.")

