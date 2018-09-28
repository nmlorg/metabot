"""Quick routines to convert machine-friendly data types to human-friendly strings."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import time as _time


def date(dtime, base=None, quiet=False):  # pylint: disable=too-many-branches
    """Convert the given datetime.date/datetime.datetime into a human-friendly string."""

    if not base:
        base = datetime.datetime.fromtimestamp(_time.time(), getattr(dtime, 'tzinfo', None)).date()
    if not quiet:
        delta = (isinstance(dtime, datetime.datetime) and dtime.date() or dtime) - base
        if delta.days == 0:
            day = 'TODAY,'
        elif delta.days == 1:
            day = 'TOMORROW,'
        elif delta.days == -1:
            day = 'YESTERDAY,'
        elif 1 < delta.days < 7:
            day = 'this'
        elif -1 > delta.days > -7:
            day = 'last'
        elif delta.days > 0:
            day = '%s on' % plural(delta.days // 7, 'week')
        else:
            day = '%s ago on' % plural(-delta.days // 7, 'week')
        day += ' '
    else:
        day = ''
    day += dtime.strftime('%a')
    mon = dtime.strftime('%b')
    if dtime.year != base.year:
        text = '%s, %s (%i) %i' % (day, mon, dtime.year, dtime.day)
    elif dtime.month != base.month:
        text = '%s, %s %i' % (day, mon, dtime.day)
    else:
        text = '%s %i' % (day, dtime.day)
    if isinstance(dtime, datetime.datetime):
        text = '%s, %s' % (text, time(dtime))
    return text


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

    text = date(start)
    if start == end:
        return text
    if isinstance(start, datetime.datetime):
        if (start.year != end.year or start.month != end.month or
                end - start >= datetime.timedelta(days=1)):
            return '%s \u2013 %s' % (text, date(end, base=start.date(), quiet=True))
        if start.day != end.day or (start.hour < 12) != (end.hour < 12):
            return '%s \u2013 %s' % (text, time(end))
        return '%s\u2013%s' % (text.rsplit(None, 1)[0], time(end))
    if start.year != end.year or start.month != end.month:
        return '%s \u2013 %s' % (text, date(end, base=start, quiet=True))
    return '%s\u2013%i' % (text, end.day)


def time(dtime):
    """Convert the given datetime.datetime/datetime.time into a human-friendly string."""

    text = '%i' % (((dtime.hour - 1) % 12) + 1)
    if dtime.minute:
        text = '%s:%02i' % (text, dtime.minute)
    return '%s %s' % (text, dtime.strftime('%P'))
