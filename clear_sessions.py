"""This file should be run at each new release to disconnect users."""
from django.contrib.sessions.models import Session

Session.objects.all().delete()
