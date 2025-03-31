import logging

import httpx
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest

from manager.models.token import create_token


def login_user(request: HttpRequest, access_token: str) -> bool:
    """
    Try to log in user, and creates the account if user do not exist.
    Return True if success, otherwise False.
    """
    graph_data = httpx.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    user_id = graph_data['id']

    user_email = graph_data.get('mail', None)
    if user_email is None:  # Can't retrieve email, login failed
        logging.info('Failed to log in user because email is missing.')
        return False

    first_name = graph_data.get('givenName', None)
    last_name = graph_data.get('surname', None)

    if first_name is None or last_name is None:
        display_name = graph_data.get('displayName', None)
        first_name, last_name = display_name.split(' ', 1)

    user = User.objects.filter(username=user_id).first()

    if not user:
        user = _create_user(user_id, user_email, first_name, last_name)

    elif not user.is_active:
        return False

    create_token(user, access_token)
    login(request, user)

    return True


def _create_user(username: str, email: str, first_name: str = None, last_name: str = None) -> User:
    if first_name is None or last_name is None:
        return User.objects.create_user(username=username, email=email, is_active=True)

    return User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, is_active=True)
