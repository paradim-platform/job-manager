from django.contrib.auth.models import User
from django.db import models


class AccessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=2550, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


def create_token(user: User, token) -> str:
    AccessToken.objects.filter(user=user).exclude(token=token).delete()  # Delete other access tokens (They are likely expired at this point)
    access_token, _ = AccessToken.objects.get_or_create(user=user, token=token)  # Ensure to have a valid access token on login

    return access_token.token


def retrieve_token(user: User) -> str | None:
    try:
        return AccessToken.objects.get(user=user).token
    except AccessToken.DoesNotExist:
        return None
