import logging

from django.conf import settings

logger = logging.getLogger('executor')
logger.setLevel(settings.LOGGING_LEVEL)
