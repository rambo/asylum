# -*- coding: utf-8 -*-
import logging
import time

from django.conf import settings
from members.models import Member
from requests.sessions import Session

from .utils import api_configured, get_client

logger = logging.getLogger()


class SlackMemberSync(object):
    """Sync members and slack members"""

    def get_slack_users_simple(self, slack, exclude_api_user=True):
        """Get just the properties we need from the slack members list"""
        response = slack.users.list()
        emails = []
        for member in response.body['members']:
            if 'email' not in member['profile']:
                # bot or similar
                continue
            if exclude_api_user and member['name'] == settings.SLACK_API_USERNAME:
                continue
            emails.append((member['id'], member['name'], member['profile']['email']))
        return emails

    def sync_members(self, autodeactivate=False):
        """Sync members, NOTE: https://github.com/ErikKalkoken/slackApiDoc/blob/master/users.admin.setInactive.md says 
        deactivation via API works only on paid tiers"""
        if not api_configured():
            raise RuntimeError("Slack API not configured")
        with Session() as session:
            slack = get_client(session=session)
            slack_users = self.get_slack_users_simple(slack)
            slack_emails = set([x[2] for x in slack_users])
            add_members = Member.objects.exclude(email__in=slack_emails)
            for member in add_members:
                try:
                    resp = slack.users.admin.invite(member.email)
                    if 'ok' not in resp.body or not resp.body['ok']:
                        self.logger.error("Could not invite {}, response: {}".format(member.email, resp.body))
                    time.sleep(0.1)  # rate-limit
                except Exception as e:
                    logger.exception("Got exception when trying to invite {}".format(member.email))

            member_emails = set(Member.objects.values_list('email', flat=True))
            remove_slack_emails = slack_emails - member_emails
            remove_usernames = []
            if not remove_slack_emails:
                return remove_usernames

            usernames_by_email = {x[2]: x[1] for x in slack_users}
            remove_usernames = [(usernames_by_email[x], x) for x in remove_slack_emails]

            if not autodeactivate:
                return remove_usernames

            userids_by_email = {x[2]: x[0] for x in slack_users}
            for email in remove_slack_emails:
                try:
                    resp = slack.users.admin.setInactive(userids_by_email[email])
                    if 'ok' not in resp.body or not resp.body['ok']:
                        self.logger.error(
                            "Could not deactivate {}, response: {}".format(email, resp.body))
                    time.sleep(0.1)  # rate-limit
                except Exception as e:
                    logger.exception("Got exception when trying to deactivate {}".format(email))

            return remove_usernames
