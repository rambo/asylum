# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Make sure all members are in Slack and optionally kick non-members'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        raise NotImplemented()
