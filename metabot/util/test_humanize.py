"""Tests for metabot.util.humanize."""

import datetime

from metabot.util import humanize


def test_humanize_date():
    """Quick tests for humanize.date."""

    base = datetime.date(2017, 11, 15)
    assert humanize.date(datetime.date(2017, 11, 15), base=base) == 'Wed 15ᵗʰ'
    assert humanize.date(datetime.date(2017, 11, 16), base=base) == 'Thu 16ᵗʰ'


def test_humanize_dayofmonth():
    """Quick tests for humanize.dayofmonth."""

    assert humanize.dayofmonth(1) == '1ˢᵗ'
    assert humanize.dayofmonth(2) == '2ⁿᵈ'
    assert humanize.dayofmonth(3) == '3ʳᵈ'
    assert humanize.dayofmonth(4) == '4ᵗʰ'
    assert humanize.dayofmonth(11) == '11ᵗʰ'
    assert humanize.dayofmonth(12) == '12ᵗʰ'
    assert humanize.dayofmonth(13) == '13ᵗʰ'
    assert humanize.dayofmonth(21) == '21ˢᵗ'


def test_nextmonth():
    """Quick tests for humanize._nextmonth."""

    # pylint: disable=protected-access
    assert humanize._nextmonth(datetime.date(2024, 11, 1)) == datetime.date(2024, 12, 1)
    assert humanize._nextmonth(datetime.date(2024, 12, 1), -1) == datetime.date(2024, 11, 1)
    assert humanize._nextmonth(datetime.date(2024, 12, 1)) == datetime.date(2025, 1, 1)
    assert humanize._nextmonth(datetime.date(2025, 1, 1), -1) == datetime.date(2024, 12, 1)

    assert humanize._nextmonth(datetime.date(2025, 1, 31), 1) == datetime.date(2025, 2, 28)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 2) == datetime.date(2025, 3, 31)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 3) == datetime.date(2025, 4, 30)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 4) == datetime.date(2025, 5, 31)

    assert humanize._nextmonth(datetime.date(2025, 5, 31), -1) == datetime.date(2025, 4, 30)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -2) == datetime.date(2025, 3, 31)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -3) == datetime.date(2025, 2, 28)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -4) == datetime.date(2025, 1, 31)


def test_humanize_howrecent():
    """Quick tests for humanize.howrecent."""

    base = datetime.datetime(2017, 11, 15, 12)
    assert humanize.howrecent(datetime.datetime(2017, 11, 15, 10),
                              datetime.datetime(2017, 11, 15, 11),
                              base=base) == 'TODAY,'
    assert humanize.howrecent(datetime.datetime(2017, 11, 15, 11),
                              datetime.datetime(2017, 11, 15, 12),
                              base=base) == 'NOW,'
    assert humanize.howrecent(datetime.datetime(2017, 11, 15, 12),
                              datetime.datetime(2017, 11, 15, 13),
                              base=base) == 'NOW,'
    assert humanize.howrecent(datetime.datetime(2017, 11, 15, 13),
                              datetime.datetime(2017, 11, 15, 14),
                              base=base) == 'TODAY,'

    yesterday = datetime.datetime(2017, 11, 14, 12)
    assert humanize.howrecent(datetime.datetime(2017, 11, 14), yesterday, base=base) == 'YESTERDAY,'
    assert humanize.howrecent(datetime.datetime(2017, 11, 13), yesterday, base=base) == '² ᵈᵃʸˢ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 9), yesterday, base=base) == '⁶ ᵈᵃʸˢ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 8), yesterday, base=base) == '¹ʷ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 2), yesterday, base=base) == '¹ʷ⁶ᵈ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 1), yesterday, base=base) == '²ʷ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2016, 11, 16), yesterday, base=base) == '¹¹ᵐ⁴ʷ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2016, 11, 15), yesterday, base=base) == '¹ʸ ᵃᵍᵒ'
    assert humanize.howrecent(datetime.datetime(2016, 10, 15), yesterday, base=base) == '¹ʸ¹ᵐ ᵃᵍᵒ'

    future = datetime.datetime(2018, 3, 30)
    assert humanize.howrecent(datetime.datetime(2017, 11, 16), future, base=base) == 'TOMORROW,'
    assert humanize.howrecent(datetime.datetime(2017, 11, 17), future, base=base) == '² ᵈᵃʸˢ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 21), future, base=base) == '⁶ ᵈᵃʸˢ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 22), future, base=base) == '¹ʷ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 28), future, base=base) == '¹ʷ⁶ᵈ'
    assert humanize.howrecent(datetime.datetime(2017, 11, 29), future, base=base) == '²ʷ'
    assert humanize.howrecent(datetime.datetime(2017, 12, 14), future, base=base) == '⁴ʷ¹ᵈ'
    assert humanize.howrecent(datetime.datetime(2017, 12, 15), future, base=base) == '¹ᵐ'
    assert humanize.howrecent(datetime.datetime(2017, 12, 16), future, base=base) == '¹ᵐ'
    assert humanize.howrecent(datetime.datetime(2017, 12, 22), future, base=base) == '¹ᵐ¹ʷ'
    assert humanize.howrecent(datetime.datetime(2018, 1, 15), future, base=base) == '²ᵐ'
    assert humanize.howrecent(datetime.datetime(2018, 1, 21), future, base=base) == '²ᵐ'
    assert humanize.howrecent(datetime.datetime(2018, 11, 14), future, base=base) == '¹¹ᵐ⁴ʷ'
    assert humanize.howrecent(datetime.datetime(2018, 11, 15), future, base=base) == '¹ʸ'
    assert humanize.howrecent(datetime.datetime(2018, 12, 14), future, base=base) == '¹ʸ'
    assert humanize.howrecent(datetime.datetime(2019, 12, 15), future, base=base) == '²ʸ¹ᵐ'


def test_humanize_list():
    """Quick tests for humanize.list."""

    assert humanize.list(['one']) == 'one'
    assert humanize.list(['one', 'two']) == 'one and two'
    assert humanize.list(['one', 'two', 'three']) == 'one, two, and three'


def test_humanize_range(monkeypatch):
    """Quick tests for humanize.range (and humanize.date/humanize.time)."""

    def _test(start, end):
        return humanize.range(start, end).replace('\u2013', '-')

    start = datetime.date(2017, 11, 15)
    start_ts = float(start.strftime('%s'))
    monkeypatch.setattr('time.time', lambda: start_ts)
    next_day = datetime.date(2017, 11, 16)
    next_week = datetime.date(2017, 11, 22)
    next_month = datetime.date(2017, 12, 15)
    next_year = datetime.date(2018, 1, 15)

    assert _test(start, start) == 'NOW, Wed 15ᵗʰ'
    assert _test(start, next_day) == 'NOW, Wed 15-16ᵗʰ'
    assert _test(start, next_week) == 'NOW, Wed 15-22ⁿᵈ'
    assert _test(start, next_month) == 'NOW, Wed 15ᵗʰ - Fri, Dec 15ᵗʰ'
    assert _test(start, next_year) == 'NOW, Wed 15ᵗʰ - Mon, Jan (2018) 15ᵗʰ'

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

    assert _test(start, next_min) == 'NOW, Wed 15ᵗʰ, 6-6:01ᵃᵐ'
    assert _test(start, next_hour) == 'NOW, Wed 15ᵗʰ, 6-7ᵃᵐ'
    assert _test(start, next_pm) == 'NOW, Wed 15ᵗʰ, 6ᵃᵐ - 6ᵖᵐ'
    assert _test(start, hours_23) == 'NOW, Wed 15ᵗʰ, 6ᵃᵐ - 5ᵃᵐ'
    assert _test(start, hours_25) == 'NOW, Wed 15ᵗʰ, 6ᵃᵐ - Thu 16ᵗʰ, 7ᵃᵐ'
    assert _test(start, next_month) == 'NOW, Wed 15ᵗʰ, 6ᵃᵐ - Fri, Dec 15ᵗʰ, 6ᵃᵐ'
    assert _test(start, next_year) == 'NOW, Wed 15ᵗʰ, 6ᵃᵐ - Mon, Jan (2018) 15ᵗʰ, 6ᵃᵐ'
