"""Tests for metabot.util.humanize."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from metabot import util


def test_humanize_list():
    """Quick tests for humanize.list."""

    assert util.humanize.list(['one']) == 'one'
    assert util.humanize.list(['one', 'two']) == 'one and two'
    assert util.humanize.list(['one', 'two', 'three']) == 'one, two, and three'


def test_humanize_range(monkeypatch):
    """Quick tests for humanize.range (and humanize.date/humanize.time)."""

    class _MockDate(datetime.date):

        @staticmethod
        def today():  # pylint: disable=missing-docstring
            return start

    monkeypatch.setattr('datetime.date', _MockDate)

    def _test(start, end):
        return util.humanize.range(start, end).replace(u'\u2013', '-')

    start = datetime.date(2017, 11, 15)
    next_day = datetime.date(2017, 11, 16)
    next_week = datetime.date(2017, 11, 22)
    next_month = datetime.date(2017, 12, 15)
    next_year = datetime.date(2018, 1, 15)

    assert _test(start, next_day) == 'Wed 15-16'
    assert _test(start, next_week) == 'Wed 15-22'
    assert _test(start, next_month) == 'Wed 15 - Fri, Dec 15'
    assert _test(start, next_year) == 'Wed 15 - Mon, Jan (2018) 15'

    start = datetime.datetime(2017, 11, 15, 6)
    next_min = datetime.datetime(2017, 11, 15, 6, 1)
    next_hour = datetime.datetime(2017, 11, 15, 7)
    next_pm = datetime.datetime(2017, 11, 15, 18)
    hours_23 = datetime.datetime(2017, 11, 16, 5)
    hours_25 = datetime.datetime(2017, 11, 16, 7)
    next_month = datetime.datetime(2017, 12, 15, 6)
    next_year = datetime.datetime(2018, 1, 15, 6)

    assert _test(start, next_min) == 'Wed 15, 6-6:01 am'
    assert _test(start, next_hour) == 'Wed 15, 6-7 am'
    assert _test(start, next_pm) == 'Wed 15, 6 am - 6 pm'
    assert _test(start, hours_23) == 'Wed 15, 6 am - 5 am'
    assert _test(start, hours_25) == 'Wed 15, 6 am - Thu 16, 7 am'
    assert _test(start, next_month) == 'Wed 15, 6 am - Fri, Dec 15, 6 am'
    assert _test(start, next_year) == 'Wed 15, 6 am - Mon, Jan (2018) 15, 6 am'
