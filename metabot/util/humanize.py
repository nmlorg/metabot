"""Quick routines to convert machine-friendly data types to human-friendly strings."""

import calendar
import datetime
import time as _time

from metabot.util import unicodeutil


def _now_copy_tz(dtime):
    now = datetime.datetime.fromtimestamp(_time.time(), getattr(dtime, 'tzinfo', None))
    return isinstance(dtime, datetime.datetime) and now or now.date()


def date(dtime, base=None):  # pylint: disable=too-many-branches
    """Convert the given datetime.date/datetime.datetime into a human-friendly string."""

    if not base:
        base = _now_copy_tz(dtime)  # pragma: no cover
    day = dtime.strftime('%a')
    mon = dtime.strftime('%b')
    dom = dayofmonth(dtime.day)
    if dtime.year != base.year:
        text = '%s, %s (%i) %s' % (day, mon, dtime.year, dom)
    elif dtime.month != base.month:
        text = '%s, %s %s' % (day, mon, dom)
    else:
        text = '%s %s' % (day, dom)
    if isinstance(dtime, datetime.datetime):
        text = '%s, %s' % (text, time(dtime))
    return text


def dayofmonth(dom):
    """Return a day of the month in ordinal form (1st, 11th, etc.)."""

    ending = 'th'
    if not 11 <= dom <= 13:
        ones = dom % 10
        if ones == 1:
            ending = 'st'
        elif ones == 2:
            ending = 'nd'
        elif ones == 3:
            ending = 'rd'
    return '%s%s' % (dom, unicodeutil.superscript(ending))


def _nextmonth(dt, months=1):
    day = dt.day

    while months > 0:
        months -= 1
        if dt.month == 12:
            year = dt.year + 1
            month = 1
        else:
            year = dt.year
            month = dt.month + 1
        _, ndays = calendar.monthrange(year, month)
        dt = dt.replace(year=year, month=month, day=min(day, ndays))
    while months < 0:
        months += 1
        if dt.month == 1:
            year = dt.year - 1
            month = 12
        else:
            year = dt.year
            month = dt.month - 1
        _, ndays = calendar.monthrange(year, month)
        dt = dt.replace(year=year, month=month, day=min(day, ndays))
    return dt


def _nextyear(dt, years=1):
    year = dt.year + years
    _, ndays = calendar.monthrange(year, dt.month)
    return dt.replace(year=year, day=min(dt.day, ndays))


def howrecent(start, end, base=None):  # pylint: disable=too-many-branches,too-many-return-statements
    """Convert the delta between start and base into a human-friendly string."""

    if not base:
        base = _now_copy_tz(start)  # pragma: no cover
    if start <= base <= end:
        return 'NOW,'
    if isinstance(base, datetime.datetime):
        start = start.date()
        base = base.date()
    delta = start - base
    if delta.days == 0:
        return 'TODAY,'
    if delta.days == 1:
        return 'TOMORROW,'
    if delta.days == -1:
        return 'YESTERDAY,'

    if start < base:
        left = start
        right = base
    else:
        left = base
        right = start

    years = 0
    left = _nextyear(left)
    while left <= right:
        years += 1
        left = _nextyear(left)
    left = _nextyear(left, -1)

    months = 0
    left = _nextmonth(left)
    while left <= right:
        months += 1
        left = _nextmonth(left)
    left = _nextmonth(left, -1)

    weeks, days = divmod((right - left).days, 7)

    if years:
        prefix = f'{years}y'
        if months:
            prefix = f'{prefix}{months}m'
    elif months:
        prefix = f'{months}m'
        if weeks:
            prefix = f'{prefix}{weeks}w'
    elif weeks:
        prefix = f'{weeks}w'
        if days:
            prefix = f'{prefix}{days}d'
    else:
        prefix = f'{days} days'

    if delta.days < 0:
        prefix += ' ago'
    return unicodeutil.superscript(prefix)


def list(arr):  # pylint: disable=redefined-builtin
    """Convert the given list into a human-friendly string."""

    if len(arr) == 1:
        return arr[0]
    if len(arr) == 2:
        return '%s and %s' % (arr[0], arr[1])
    return '%s, and %s' % (', '.join(arr[:-1]), arr[-1])


def plural(num, noun, fmtstr='%s %s'):
    """Return '1 noun', '2 nouns', etc."""

    if num == 1:
        return fmtstr % (num, noun)
    return fmtstr % (num, noun + 's')


def range(start, end):  # pylint: disable=redefined-builtin
    """Convert the given datetime.date/datetime.datetime objects into a human-friendly string."""

    now = _now_copy_tz(start)
    text = '%s %s' % (howrecent(start, end, base=now), date(start, base=now))
    if start == end:
        return text
    if isinstance(start, datetime.datetime):
        if (start.year != end.year or start.month != end.month or
                end - start >= datetime.timedelta(days=1)):
            return '%s \u2013 %s' % (text, date(end, base=start.date()))
        if start.day != end.day or (start.hour < 12) != (end.hour < 12):
            return '%s \u2013 %s' % (text, time(end))
        return '%s\u2013%s' % (text[:-2], time(end))
    if start.year != end.year or start.month != end.month:
        return '%s \u2013 %s' % (text, date(end, base=start))
    return '%s\u2013%s' % (text[:-2], dayofmonth(end.day))


def time(dtime):
    """Convert the given datetime.datetime/datetime.time into a human-friendly string."""

    text = '%i' % (((dtime.hour - 1) % 12) + 1)
    if dtime.minute:
        text = '%s:%02i' % (text, dtime.minute)
    return text + unicodeutil.superscript(dtime.strftime('%P'))
