# -*- coding: utf-8 -*-

import csv

from django.core.management.base import BaseCommand, CommandError
from access.models import Token, AccessType, Grant, TokenType
from members.models import Member

class Command(BaseCommand):
    help = 'Exports tokens and their access controls to sqlite file'

    def add_arguments(self, parser):
        parser.add_argument('filepath')
        parser.add_argument('tokentype')
        parser.add_argument('accessids')

    def handle(self, *args, **options):
        ttype = TokenType.objects.get(pk=int(options['tokentype']))
        atype_ids = [ int(x) for x in options['accessids'].split(',') ]
        grant_atypes = AccessType.objects.filter(pk__in=atype_ids)

        with open(options['filepath'], 'rt') as fp:
            reader =  csv.reader(fp, delimiter=";")
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                if Token.objects.filter(value=row[0]).count():
                    if options['verbosity'] > 0:
                        print("Card %s already exists" % row[0])
                    continue
                if not Member.objects.filter(email=row[1]).count():
                    if options['verbosity'] > 0:
                        print("Member with email %s not found" % row[1])
                    continue
                member = Member.objects.get(email=row[1])
                token = Token(owner=member, value=row[0], ttype=ttype)
                if row[2] == 'True':
                    token.revoked = True
                token.save()
                if options['verbosity'] > 0:
                    print("Created token %s" % token)
                for access in grant_atypes:
                    grant, created = Grant.objects.get_or_create(owner=member, atype=access)
                    if created:
                        if options['verbosity'] > 0:
                            print("Created grant %s" % (grant))
