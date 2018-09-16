"""Quick routines to convert machine-friendly data types to human-friendly strings."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import time as _time


def date(dtime, today=None):
    """Convert the given datetime.date/datetime.datetime into a human-friendly string."""

    if not today:
        today = datetime.datetime.fromtimestamp(_time.time(), getattr(dtime, 'tzinfo', None)).date()
    day = dtime.strftime('%a')
    mon = dtime.strftime('%b')
    if dtime.year != today.year:
        text = '%s, %s (%i) %i' % (day, mon, dtime.year, dtime.day)
    elif dtime.month != today.month:
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


def range(start, end):  # pylint: disable=redefined-builtin
    """Convert the given datetime.date/datetime.datetime objects into a human-friendly string."""

    text = date(start)
    if start == end:
        return text
    if isinstance(start, datetime.datetime):
        if (start.year != end.year or start.month != end.month or
                end - start >= datetime.timedelta(days=1)):
            return '%s \u2013 %s' % (text, date(end, today=start))
        if start.day != end.day or (start.hour < 12) != (end.hour < 12):
            return '%s \u2013 %s' % (text, time(end))
        return '%s\u2013%s' % (text.rsplit(None, 1)[0], time(end))
    if start.year != end.year or start.month != end.month:
        return '%s \u2013 %s' % (text, date(end, today=start))
    return '%s\u2013%i' % (text, end.day)


def time(dtime):
    """Convert the given datetime.datetime/datetime.time into a human-friendly string."""

    text = '%i' % (((dtime.hour - 1) % 12) + 1)
    if dtime.minute:
        text = '%s:%02i' % (text, dtime.minute)
    return '%s %s' % (text, dtime.strftime('%P'))
