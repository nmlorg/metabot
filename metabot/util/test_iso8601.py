"""Tests for metabot.util.iso8601."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import iso8601


def test_basic():
    """Quick tests for totimestamp."""

    assert iso8601.totimestamp('1970-01-01') == 0
    assert iso8601.totimestamp('1970-01-01T0:00:00') == 0
    assert iso8601.totimestamp('1970-01-01T0:00:00-0:00') == 0
    assert iso8601.totimestamp('1970-01-01T0:00:00+0:00') == 0
    assert iso8601.totimestamp('1970-01-01T0:00:00Z') == 0

    assert iso8601.totimestamp('1970-01-01T0:00:00-07:00') == 7 * 60 * 60
    assert iso8601.totimestamp('2018-09-09T22:02:15-07:00') == 1536555735
    assert iso8601.totimestamp('2018-09-10T10:35:29+05:30') == 1536555929
