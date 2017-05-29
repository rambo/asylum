# -*- coding: utf-8 -*-
from django.conf import settings
from members.objects import Member
from requests.sessions import Session

from .utils import api_configured, get_client

logger = logger.getLogger()


class SlackMemberSync(object):
    def get_slack_users_simple(self, slack, exclude_api_user=True):
        response = slack.users.list()
        emails = []
        for member in response.body['members']:
            if 'email' not in memeber['profile']:
                # bot or similar
                continue
            if exclude_api_user and member['name'] == settings.SLACK_API_USERNAME:
                continue
            emails.append((member['id'], member['name'], member['profile']['email']))
        return emails

    def sync_members(self, autodeactivate=False):
        """Sync members, NOTE: https://github.com/ErikKalkoken/slackApiDoc/blob/master/users.admin.setInactive.md says 
        deactivation via API works only on paid tiers"""
        with Session() as session:
            slack = get_client(session=session)
            slack_users = self.get_slack_users_simple(slack)
            slac_emails = [x[2] for x in slack_users]
            add_members = Member.objects.exclude(email__in=slack_emails)
            for member in add_members:
                try:
                    resp = slack.users.admin.invite(member.email)
                    if 'ok' not in resp.body or not resp.body['ok']:
                        self.logger.error("Could not invite {}, response: {}".format(member.email, response.body))
                except Exception as e:
                    logger.exception("Got exception when trying to invite {}".format(member.email))
            # TODO: check which members should be removed
