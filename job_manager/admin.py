import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


@staff_member_required
def admin_cache_management_view(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Cache Management',
    }
    return render(request, 'admin/cache_management.html', context)


@staff_member_required
def clear_cache(_: HttpRequest) -> HttpResponse:
    cache.clear()
    logging.info('Cache has been cleared.')

    return redirect('admin-cache-management')
