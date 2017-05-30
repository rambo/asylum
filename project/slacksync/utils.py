# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from slacker import Slacker

logger = logging.getLogger()


def api_configured():
    """Check that Slack API settings are configured"""
    return bool(settings.SLACK_APIKEY) and bool(settings.SLACK_API_USERNAME)


def get_client(**kwargs):
    """Get a Slacker instance"""
    if not api_configured():
        return False
    return Slacker(settings.SLACK_APIKEY, **kwargs)


def quick_invite(email):
    """Quickly invite single email"""
    if not api_configured():
        return False
    slack = get_client()
    try:
        resp = slack.users.admin.invite(member.email)
        if 'ok' not in resp.body or not resp.body['ok']:
            self.logger.error("Could not invite {}, response: {}".format(email, response.body))
            return False
    except Exception as e:
        logger.exception("Got exception when trying to invite {}".format(email))
        return False
    return True
