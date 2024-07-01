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
    assert humanize._nextmonth(datetime.date(2024, 11, 1), 1) == datetime.date(2024, 12, 1)
    assert humanize._nextmonth(datetime.date(2024, 12, 1), -1) == datetime.date(2024, 11, 1)
    assert humanize._nextmonth(datetime.date(2024, 12, 1), 1) == datetime.date(2025, 1, 1)
    assert humanize._nextmonth(datetime.date(2025, 1, 1), -1) == datetime.date(2024, 12, 1)

    assert humanize._nextmonth(datetime.date(2025, 1, 31), 1) == datetime.date(2025, 2, 28)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 2) == datetime.date(2025, 3, 31)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 3) == datetime.date(2025, 4, 30)
    assert humanize._nextmonth(datetime.date(2025, 1, 31), 4) == datetime.date(2025, 5, 31)

    assert humanize._nextmonth(datetime.date(2025, 5, 31), -1) == datetime.date(2025, 4, 30)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -2) == datetime.date(2025, 3, 31)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -3) == datetime.date(2025, 2, 28)
    assert humanize._nextmonth(datetime.date(2025, 5, 31), -4) == datetime.date(2025, 1, 31)


def test_nextyear():
    """Quick tests for humanize._nextyear."""

    # pylint: disable=protected-access
    assert humanize._nextyear(datetime.date(2024, 11, 1), 1) == datetime.date(2025, 11, 1)
    assert humanize._nextyear(datetime.date(2025, 11, 1), -1) == datetime.date(2024, 11, 1)

    assert humanize._nextyear(datetime.date(2024, 2, 29), 1) == datetime.date(2025, 2, 28)
    assert humanize._nextyear(datetime.date(2024, 2, 29), 2) == datetime.date(2026, 2, 28)
    assert humanize._nextyear(datetime.date(2024, 2, 29), 3) == datetime.date(2027, 2, 28)
    assert humanize._nextyear(datetime.date(2024, 2, 29), 4) == datetime.date(2028, 2, 29)

    assert humanize._nextyear(datetime.date(2028, 2, 29), -1) == datetime.date(2027, 2, 28)
    assert humanize._nextyear(datetime.date(2028, 2, 29), -2) == datetime.date(2026, 2, 28)
    assert humanize._nextyear(datetime.date(2028, 2, 29), -3) == datetime.date(2025, 2, 28)
    assert humanize._nextyear(datetime.date(2028, 2, 29), -4) == datetime.date(2024, 2, 29)


def test_humanize_howrecent():
    """Quick tests for humanize.howrecent."""

    def _test(*spec):
        return humanize.howrecent(datetime.datetime(2017, 11, 15, 12),
                                  datetime.datetime(2017, 11, 15, 13),
                                  base=datetime.datetime(*spec))

    assert _test(2015, 10, 15) == '²ʸ¹ᵐ'
    assert _test(2015, 10, 16) == '²ʸ'
    assert _test(2015, 11, 15) == '²ʸ'
    assert _test(2016, 11, 15) == '¹ʸ'
    assert _test(2016, 11, 16) == '¹¹ᵐ⁴ʷ'
    assert _test(2017, 9, 15) == '²ᵐ'
    assert _test(2017, 10, 8) == '¹ᵐ¹ʷ'
    assert _test(2017, 10, 9) == '¹ᵐ'
    assert _test(2017, 10, 15) == '¹ᵐ'
    assert _test(2017, 10, 16) == '⁴ʷ²ᵈ'
    assert _test(2017, 11, 1) == '²ʷ'
    assert _test(2017, 11, 2) == '¹ʷ⁶ᵈ'
    assert _test(2017, 11, 8) == '¹ʷ'
    assert _test(2017, 11, 9) == '⁶ ᵈᵃʸˢ'
    assert _test(2017, 11, 13) == '² ᵈᵃʸˢ'
    assert _test(2017, 11, 14) == 'ᵗᵒᵐᵒʳʳᵒʷ'
    assert _test(2017, 11, 14, 23, 50) == 'ᵗᵒᵐᵒʳʳᵒʷ'

    assert _test(2017, 11, 15) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 9) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 9, 30) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 10) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 10, 30) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 10, 50) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 11) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 11, 30) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 11, 50) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 12) == '⭐ ᴺᴼᵂ'
    assert _test(2017, 11, 15, 12, 30) == '⭐ ᴺᴼᵂ'
    assert _test(2017, 11, 15, 13) == '⭐ ᴺᴼᵂ'
    assert _test(2017, 11, 15, 13, 10) == 'ᵗᵒᵈᵃʸ'
    assert _test(2017, 11, 15, 14) == 'ᵗᵒᵈᵃʸ'

    assert _test(2017, 11, 16) == 'ʸᵉˢᵗᵉʳᵈᵃʸ'
    assert _test(2017, 11, 17) == '² ᵈᵃʸˢ ᵃᵍᵒ'
    assert _test(2017, 11, 21) == '⁶ ᵈᵃʸˢ ᵃᵍᵒ'
    assert _test(2017, 11, 22) == '¹ʷ ᵃᵍᵒ'
    assert _test(2017, 11, 28) == '¹ʷ⁶ᵈ ᵃᵍᵒ'
    assert _test(2017, 11, 29) == '²ʷ ᵃᵍᵒ'
    assert _test(2018, 11, 14) == '¹¹ᵐ⁴ʷ ᵃᵍᵒ'
    assert _test(2018, 11, 15) == '¹ʸ ᵃᵍᵒ'
    assert _test(2018, 12, 15) == '¹ʸ¹ᵐ ᵃᵍᵒ'


def test_humanize_list():
    """Quick tests for humanize.list."""

    assert humanize.list(['one']) == 'one'
    assert humanize.list(['one', 'two']) == 'one and two'
    assert humanize.list(['one', 'two', 'three']) == 'one, two, and three'


def test_humanize_range(monkeypatch):
    """Quick tests for humanize.range (and humanize.date/humanize.time)."""

    def _test(start, end):
        return humanize.range(start, end)

    start = datetime.date(2017, 11, 15)
    start_ts = float(start.strftime('%s'))
    monkeypatch.setattr('time.time', lambda: start_ts)
    next_day = datetime.date(2017, 11, 16)
    next_week = datetime.date(2017, 11, 22)
    next_month = datetime.date(2017, 12, 15)
    next_year = datetime.date(2018, 1, 15)

    assert _test(start, start) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ'
    assert _test(start, next_day) == '⭐ ᴺᴼᵂ Wed 15–16ᵗʰ'
    assert _test(start, next_week) == '⭐ ᴺᴼᵂ Wed 15–22ⁿᵈ'
    assert _test(start, next_month) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ – Fri, Dec 15ᵗʰ'
    assert _test(start, next_year) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ – Mon, Jan (2018) 15ᵗʰ'

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

    assert _test(start, next_min) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6–6:01ᵃᵐ'
    assert _test(start, next_hour) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6–7ᵃᵐ'
    assert _test(start, next_pm) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6ᵃᵐ – 6ᵖᵐ'
    assert _test(start, hours_23) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6ᵃᵐ – 5ᵃᵐ'
    assert _test(start, hours_25) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6ᵃᵐ – Thu 16ᵗʰ, 7ᵃᵐ'
    assert _test(start, next_month) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6ᵃᵐ – Fri, Dec 15ᵗʰ, 6ᵃᵐ'
    assert _test(start, next_year) == '⭐ ᴺᴼᵂ Wed 15ᵗʰ, 6ᵃᵐ – Mon, Jan (2018) 15ᵗʰ, 6ᵃᵐ'
