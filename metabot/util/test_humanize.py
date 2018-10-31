"""Tests for metabot.util.humanize."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

from metabot.util import humanize


def test_humanize_date():
    """Quick tests for humanize.date."""

    base = datetime.date(2017, 11, 15)
    assert humanize.date(datetime.date(2017, 11, 15), base=base) == 'TODAY, Wed 15'

    assert humanize.date(datetime.date(2017, 11, 14), base=base) == 'YESTERDAY, Tue 14'
    assert humanize.date(datetime.date(2017, 11, 13), base=base) == 'last Mon 13'
    assert humanize.date(datetime.date(2017, 11, 9), base=base) == 'last Thu 9'
    assert humanize.date(datetime.date(2017, 11, 8), base=base) == '1 week ago on Wed 8'
    assert humanize.date(datetime.date(2017, 11, 1), base=base) == '2 weeks ago on Wed 1'

    assert humanize.date(datetime.date(2017, 11, 16), base=base) == 'TOMORROW, Thu 16'
    assert humanize.date(datetime.date(2017, 11, 17), base=base) == 'this Fri 17'
    assert humanize.date(datetime.date(2017, 11, 17), base=base) == 'this Fri 17'
    assert humanize.date(datetime.date(2017, 11, 22), base=base) == '1 week on Wed 22'
    assert humanize.date(datetime.date(2017, 11, 29), base=base) == '2 weeks on Wed 29'


def test_humanize_list():
    """Quick tests for humanize.list."""

    assert humanize.list(['one']) == 'one'
    assert humanize.list(['one', 'two']) == 'one and two'
    assert humanize.list(['one', 'two', 'three']) == 'one, two, and three'


def test_humanize_range(monkeypatch):
    """Quick tests for humanize.range (and humanize.date/humanize.time)."""

    def _test(start, end):
        return humanize.range(start, end).replace(u'\u2013', '-')

    start = datetime.date(2017, 11, 15)
    start_ts = float(start.strftime('%s'))
    monkeypatch.setattr('time.time', lambda: start_ts)
    next_day = datetime.date(2017, 11, 16)
    next_week = datetime.date(2017, 11, 22)
    next_month = datetime.date(2017, 12, 15)
    next_year = datetime.date(2018, 1, 15)

    assert _test(start, start) == 'TODAY, Wed 15'
    assert _test(start, next_day) == 'TODAY, Wed 15-16'
    assert _test(start, next_week) == 'TODAY, Wed 15-22'
    assert _test(start, next_month) == 'TODAY, Wed 15 - Fri, Dec 15'
    assert _test(start, next_year) == 'TODAY, Wed 15 - Mon, Jan (2018) 15'

    start = datetime.datetime(2017, 11, 15, 6)
    start_ts = float(start.strftime('%s'))
    monkeypatch.setattr('time.time', lambda: start_ts)
    next_min = datetime.datetime(2017, 11, 15, 6, 1)
    next_hour = datetime.datetime(2017, 11, 15, 7)
    next_pm = datetime.datetime(2017, 11, 15, 18)
    hours_23 = datetime.datetime(2017, 11, 16, 5)
    hours_25 = datetime.datetime(2017, 11, 16, 7)
    next_month = datetime.datetime(2017, 12, 15, 6)
    next_year = datetime.datetime(2018, 1, 15, 6)

    assert _test(start, next_min) == 'TODAY, Wed 15, 6-6:01 am'
    assert _test(start, next_hour) == 'TODAY, Wed 15, 6-7 am'
    assert _test(start, next_pm) == 'TODAY, Wed 15, 6 am - 6 pm'
    assert _test(start, hours_23) == 'TODAY, Wed 15, 6 am - 5 am'
    assert _test(start, hours_25) == 'TODAY, Wed 15, 6 am - Thu 16, 7 am'
    assert _test(start, next_month) == 'TODAY, Wed 15, 6 am - Fri, Dec 15, 6 am'
    assert _test(start, next_year) == 'TODAY, Wed 15, 6 am - Mon, Jan (2018) 15, 6 am'
