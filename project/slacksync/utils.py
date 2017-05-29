# -*- coding: utf-8 -*-
from django.conf import settings
from slacker import Slacker


def api_configured():
    return bool(settings.SLACK_APIKEY) and bool(settings.SLACK_API_USERNAME)


def get_client(**kwargs):
    if not api_configured():
        return False
    return Slacker(settings.SLACK_APIKEY, **kwargs)
