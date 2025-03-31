import os
from typing import Callable

import msal
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from .users import login_user


def azure_ad_middleware(get_response: Callable):
    def middleware(request: HttpRequest):
        if request.path.startswith('/launcher/'):
            if 'auth_flow' not in request.session:
                app = get_msal_app()
                auth_flow = app.initiate_auth_code_flow(['User.Read'], redirect_uri=settings.OAUTH_REDIRECT_URL)
                request.session['auth_flow'] = auth_flow

                return redirect(auth_flow['auth_uri'])

            if not request.user.is_authenticated:
                app = get_msal_app()
                auth_flow = request.session['auth_flow']

                if 'error' in request.GET:
                    return HttpResponse(
                        f"Authorization failed: {request.GET['error']} - {request.GET.get('error_description', '')}"
                    )

                try:
                    result = app.acquire_token_by_auth_code_flow(auth_flow, request.GET)

                    if 'access_token' in result:
                        login_successful = login_user(request=request, access_token=result['access_token'])

                        if not login_successful:
                            return HttpResponseForbidden('Failed to login. User is likely not active. Contact administrators for support.')

                        request.session['has_refreshed_once'] = False  # reset the refresh counter

                        return redirect(reverse('launcher'))

                    else:
                        return HttpResponse(f"Login failed: {result.get('error_description', 'Unknown error')}", status=400)

                except (KeyError, ValueError) as e:
                    logout(request)  # logout user and clear session

                    if not request.session.get('has_refreshed_once', False):
                        request.session['has_refreshed_once'] = True
                        return redirect(reverse('launcher'))

                    return HttpResponse(f'Error in auth code flow: {e}. Reloading might fix the issue.', status=400)

        return get_response(request)

    return middleware


def get_msal_app():
    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'job_manager.settings.dev':
        # When in dev mode (OAUTH_REDIRECT_URL to localhost), the AzureAD is considered Public
        return msal.PublicClientApplication(
            settings.OAUTH_CLIENT_ID,
            authority=settings.OAUTH_AUTHORITY_URL,
        )

    return msal.ConfidentialClientApplication(
        settings.OAUTH_CLIENT_ID,
        client_credential=settings.OAUTH_CLIENT_SECRET,
        authority=settings.OAUTH_AUTHORITY_URL,
    )
