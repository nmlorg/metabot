"""Tests for metabot.calendars.base (using static.Calendar instead of a local class)."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.calendars import static


def test_client():
    """Test base.Calendar (via static.Calendar) as a consumer."""

    calendar = static.Calendar('static:dummy')
    assert calendar.last_update is None

    assert calendar.add({
        'start': 2000,
        'end': 3000,
    }) == {
        'description': '',
        'end': 3000,
        'id': '1',
        'local_id': 'c2cf0008:356a192b',
        'location': '',
        'start': 2000,
        'summary': '',
        'updated': 1001,
    }
    assert calendar.last_update == 1001

    assert calendar.update('c2cf0008:356a192b', {'location': 'Dummy\nLocation'}) == {
        'description': '',
        'end': 3000,
        'id': '1',
        'local_id': 'c2cf0008:356a192b',
        'location': 'Dummy, Location',
        'start': 2000,
        'summary': '',
        'updated': 1002,
    }
    assert calendar.last_update == 1002

    assert calendar.update('c2cf0008:356a192b', {'location': 'TBD'}) == {
        'description': '',
        'end': 3000,
        'id': '1',
        'local_id': 'c2cf0008:356a192b',
        'location': '',
        'start': 2000,
        'summary': '',
        'updated': 1003,
    }
    assert calendar.last_update == 1003

    calendar.remove('c2cf0008:356a192b')


def test_server():
    """Test base.Calendar (via static.Calendar) as a data provider."""

    calendar = static.Calendar('static:dummy')
    assert calendar.calcode == 'c2cf0008'
    assert calendar.events == {}
    assert calendar.last_update is None

    # pylint: disable=protected-access

    assert calendar._updated({
        'id': 'alpha',
        'start': 2000,
        'end': 3000,
        'updated': 4000,
    })

    assert calendar.events == {
        'c2cf0008:be76331b': {
            'description': '',
            'end': 3000,
            'id': 'alpha',
            'local_id': 'c2cf0008:be76331b',
            'location': '',
            'start': 2000,
            'summary': '',
            'updated': 4000,
        },
    }

    assert calendar._updated({
        'id': 'alpha',
        'start': 2000,
        'end': 5000,
        'updated': 6000,
    })

    assert calendar.events == {
        'c2cf0008:be76331b': {
            'description': '',
            'end': 5000,
            'id': 'alpha',
            'local_id': 'c2cf0008:be76331b',
            'location': '',
            'start': 2000,
            'summary': '',
            'updated': 6000,
        },
    }

    assert not calendar._updated({
        'id': 'alpha',
        'start': 2000,
        'end': 5000,
        'updated': 6000,
    })

    assert calendar._removed('alpha')
    assert calendar.events == {}
    assert not calendar._removed('alpha')
