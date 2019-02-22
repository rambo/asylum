# -*- coding: utf-8 -*-
import calendar
import datetime
from django.utils import timezone

import pytest
import pytz
from creditor.tests.fixtures.recurring import KeyholderfeeFactory, MembershipfeeFactory, QuarterlyFactory


def year_start_end(timescope=None):
    if timescope is None:
        timescope = datetime.datetime.now()
    start = datetime.datetime(timescope.year, 1, 1).date()
    end = datetime.datetime(start.year, 12, calendar.monthrange(start.year, 12)[1]).date()
    return (start, end)


def quarter_start_end(timescope=None):
    if timescope is None:
        timescope = datetime.datetime.now()
    if timescope.month in range(1,4):
        start = datetime.datetime(timescope.year, 1, 1).date()
    elif timescope.month in range(4,7):
        start = datetime.datetime(timescope.year, 4, 1).date()
    elif timescope.month in range(7,10):
        start = datetime.datetime(timescope.year, 7, 1).date()
    else:
        start = datetime.datetime(timescope.year, 10, 1).date()
    end_month = start.month + 3
    end = datetime.datetime(start.year, end_month, calendar.monthrange(start.year, end_month)[1]).date()
    return (start, end)


def month_start_end(timescope=None):
    if timescope is None:
        timescope = timezone.now()
    start = datetime.datetime(timescope.year, timescope.month, 1).date()
    end = datetime.datetime(start.year, start.month, calendar.monthrange(start.year, start.month)[1]).date()
    return (start, end)


@pytest.mark.django_db
def test_yearly_in_scope_with_end():
    now = timezone.now()
    start, end = year_start_end(now)
    for x in range(5):
        t = MembershipfeeFactory(start=start, end=end)
        assert t.in_timescope(now)
        ret1 = t.conditional_add_transaction(now)
        assert ret1
        ret2 = t.conditional_add_transaction(now)
        assert not ret2


@pytest.mark.django_db
def test_yearly_in_scope_without_end():
    now = timezone.now()
    start, end = year_start_end(now - datetime.timedelta(weeks=60))
    end = None
    for x in range(5):
        t = MembershipfeeFactory(start=start, end=end)
        assert t.in_timescope(now)
        ret1 = t.conditional_add_transaction(now)
        assert ret1
        ret2 = t.conditional_add_transaction(now)
        assert not ret2


@pytest.mark.django_db
def test_yearly_not_in_scope_ended():
    now = timezone.now()
    start, end = year_start_end(now - datetime.timedelta(weeks=60))
    t = MembershipfeeFactory(start=start, end=end)
    assert not t.in_timescope(now)
    ret2 = t.conditional_add_transaction(now)
    assert not ret2


@pytest.mark.django_db
def test_yearly_not_in_scope_notstarted():
    now = timezone.now()
    start, end = year_start_end(now + datetime.timedelta(weeks=60))
    t = MembershipfeeFactory(start=start, end=end)
    assert not t.in_timescope(now)
    ret2 = t.conditional_add_transaction(now)
    assert not ret2


@pytest.mark.django_db
def test_quarterly_in_scope_with_end():
    now = timezone.now()

    start, end = quarter_start_end(now)
    end += datetime.timedelta(weeks=15)
    t = QuarterlyFactory(start=start, end=end)
    assert t.in_timescope(now)


@pytest.mark.django_db
def test_quarterly_in_scope_without_end():
    now = timezone.now()

    start, end = month_start_end(now - datetime.timedelta(weeks=15))
    end = None
    t = QuarterlyFactory(start=start, end=end)
    assert t.in_timescope(now)

@pytest.mark.django_db
def test_quarterly_not_in_scope_ended():
    now = timezone.now()

    start, end = month_start_end(now - datetime.timedelta(weeks=25))
    t = QuarterlyFactory(start=start, end=end)
    assert not t.in_timescope(now)

@pytest.mark.django_db
def test_quarterly_not_in_scope_notstarted():
    now = timezone.now()

    start, end = month_start_end(now + datetime.timedelta(weeks=25))
    t = QuarterlyFactory(start=start, end=end)
    assert not t.in_timescope(now)

@pytest.mark.django_db
def test_monthly_in_scope_with_end():
    now = timezone.now()

    start, end = month_start_end(now)
    end += datetime.timedelta(weeks=6)
    t = KeyholderfeeFactory(start=start, end=end)
    assert t.in_timescope(now)


@pytest.mark.django_db
def test_monthly_in_scope_without_end():
    now = timezone.now()

    start, end = month_start_end(now - datetime.timedelta(weeks=6))
    end = None
    t = KeyholderfeeFactory(start=start, end=end)
    assert t.in_timescope(now)


@pytest.mark.django_db
def test_monthly_not_in_scope_ended():
    now = timezone.now()

    start, end = month_start_end(now - datetime.timedelta(weeks=10))
    t = KeyholderfeeFactory(start=start, end=end)
    assert not t.in_timescope(now)


@pytest.mark.django_db
def test_monthly_not_in_scope_notstarted():
    now = timezone.now()

    start, end = month_start_end(now + datetime.timedelta(weeks=10))
    t = KeyholderfeeFactory(start=start, end=end)
    assert not t.in_timescope(now)
