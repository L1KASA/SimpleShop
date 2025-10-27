from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


def new_users_handler(backend, user, response, *args, **kwargs):
    try:
        user = get_user_model().objects.get(email=user.email)
    except get_user_model().DoesNotExist:
        user = get_user_model().objects.create(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        group = Group.objects.filter(name='social').first()
        if group:
            user.groups.add(group)

    social_user = user.social_auth.filter(provider=backend.name).first()

    if social_user is None:
        raise ValueError("Social user is None. Cannot find the provider for this user.")
