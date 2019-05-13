"""Quick and dirty ISO 8601 -> timestamp converter."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import re


def totimestamp(isoformat):
    """Convert a string like YYYY-MM-DDTHH:MM:SS+HH:MM to the number of seconds since 1970-01-01."""

    year, month, day, _, hour, minute, second, fraction, _, utchour, utcminute = re.match(
        r'(\d{4})-?(\d{1,2})-?(\d{1,2})'
        r'(T(\d{1,2}):?(\d{1,2}):?(\d{1,2})'
        r'([.]\d+)?'
        r'(([-+]\d{1,2}):?(\d{1,2})|Z)?'
        r')?$', isoformat).groups()
    dtime = datetime.datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0),
                              int(second or 0), int(1000000 * float(fraction or 0)))
    if utchour and utcminute:
        tzinfo = _TimeZone(int(utchour) + float(utcminute) / 60)
    else:
        tzinfo = _UTC
    return (dtime.replace(tzinfo=tzinfo) - _EPOCH).total_seconds()


class _TimeZone(datetime.tzinfo):
    __slots__ = ('_utcoffset',)

    def __init__(self, utcoffset):
        super(_TimeZone, self).__init__()
        self._utcoffset = datetime.timedelta(hours=utcoffset)

    @staticmethod
    def tzname(unused_dt):  # pragma: no cover
        return 'x'

    def utcoffset(self, unused_dt):
        return self._utcoffset

    @staticmethod
    def dst(unused_dt):  # pragma: no cover
        return datetime.timedelta(0)


_UTC = _TimeZone(0)
_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=_UTC)
