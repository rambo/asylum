# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from slacksync.membersync import SlackMemberSync
from slacksync.utils import api_configured


class Command(BaseCommand):
    help = 'Make sure all members are in Slack and optionally kick non-members'

    def add_arguments(self, parser):
        parser.add_argument('--autodeactivate', action='store_true', help='Automatically deactivate users that are no longer members')
        parser.add_argument('--noresend', action='store_true', help='Automatically deactivate users that are no longer members')

        pass

    def handle(self, *args, **options):
        if not api_configured():
            raise CommandError("API not configured")
        autoremove = False
        if options['autodeactivate']:
            autoremove = True
        resend = True
        if options['noresend']:
            resend = False
        sync = SlackMemberSync()
        tbd = sync.sync_members(autoremove, )
        if options['verbosity'] > 1:
            for dm in tbd:
                if autoremove:
                    print("User {uid} ({email}) was removed".format(uid=dm[0], email=dm[1]))
                else:
                    print("User {uid} ({email}) should be removed".format(uid=dm[0], email=dm[1]))
