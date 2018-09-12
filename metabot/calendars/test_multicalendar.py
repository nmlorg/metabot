"""Tests for metabot.calendars.multicalendar."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections

from metabot.calendars import multicalendar


def test_multicalendar(monkeypatch):
    """Run through most of the functionality of multicalendar.MultiCalendar."""

    multical = multicalendar.MultiCalendar()
    assert multical.calendars == {}
    assert multical.by_local_id == {}
    assert multical.ordered == []

    events = {
        'alpha': {
            'end': 3000,
            'local_id': 'alpha',
            'start': 2000,
            'summary': 'Alpha',
        },
        'bravo': {
            'end': 7000,
            'local_id': 'bravo',
            'start': 5000,
            'summary': 'Bravo',
        },
        'charlie': {
            'end': 8000,
            'local_id': 'charlie',
            'start': 6000,
            'summary': 'Charlie',
        },
    }
    dummycal = collections.namedtuple('_', 'events poll')(events, lambda: True)

    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        multical.add('dummy:dummy')

    assert multical.by_local_id == {'alpha': 0, 'bravo': 1, 'charlie': 2}
    assert multical.get_event('unset') == (None, None, None)
    assert multical.get_event('alpha') == (None, events['alpha'], events['bravo'])
    assert multical.get_event('bravo') == (events['alpha'], events['bravo'], events['charlie'])
    assert multical.get_event('charlie') == (events['bravo'], events['charlie'], None)

    #            |2000 3000|
    # |1000 1999|
    assert list(multical.get_overlap(1000, 1999)) == []

    #            |2000 3000|
    # |1000  2000|
    assert list(multical.get_overlap(1000, 2000)) == [events['alpha']]

    #            |2000 3000|
    # |1000                       4000|
    assert list(multical.get_overlap(1000, 4000)) == [events['alpha']]

    #            |2000 3000|
    #                      |3000  4000|
    assert list(multical.get_overlap(3000, 4000)) == [events['alpha']]

    #            |2000 3000|
    #                       |3001 4000|
    assert list(multical.get_overlap(3001, 4000)) == []

    assert list(multical.get_overlap(5000, 8000)) == [events['bravo'], events['charlie']]

    by_local_id = multical.by_local_id
    ordered = multical.ordered
    assert multical.poll()
    assert multical.by_local_id is not by_local_id and multical.by_local_id == by_local_id
    assert multical.ordered is not ordered and multical.ordered == ordered


def test_current_index(monkeypatch):  # pylint: disable=too-many-statements
    """Test the specific behavior of _current_index and current_index."""

    events = {
        'alpha': {
            'end': 3000,
            'local_id': 'alpha',
            'start': 2000,
            'summary': 'Alpha',
        },
        'bravo': {
            'end': 7000,
            'local_id': 'bravo',
            'start': 5000,
            'summary': 'Bravo',
        },
        'charlie': {
            'end': 8000,
            'local_id': 'charlie',
            'start': 6000,
            'summary': 'Charlie',
        },
    }
    dummycal = collections.namedtuple('_', 'events')(events)

    # pylint: disable=protected-access

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 1000.)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['alpha']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 3000.)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['alpha']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 3000.5)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['bravo']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 7000.)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['bravo']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 7000.5)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['charlie']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 8000.)
        multical.add('dummy:dummy')
    assert multical._current_index == multical.by_local_id['charlie']

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 8000.5)
        multical.add('dummy:dummy')
    assert multical._current_index is None

    multical = multicalendar.MultiCalendar()
    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal)
        monkey.setattr('time.time', lambda: 1000.)
        multical.add('dummy:dummy')
        assert multical.current_index == multical.by_local_id['alpha']
        assert multical.current_local_id == 'alpha'
        monkey.setattr('time.time', lambda: 3000.)
        assert multical.current_local_id == 'alpha'
        monkey.setattr('time.time', lambda: 3000.5)
        assert multical.current_local_id == 'bravo'
        monkey.setattr('time.time', lambda: 8000.)
        assert multical.current_local_id == 'charlie'
        assert multical.get_event() == (events['bravo'], events['charlie'], None)
        monkey.setattr('time.time', lambda: 8000.5)
        assert multical.current_index is None
        assert multical.current_local_id is None
        assert multical.get_event() == (None, None, None)


def test_view(monkeypatch):
    """Run through the behavior of multicalendar.View (via multicalendar.MultiCalendar.view)."""

    multical = multicalendar.MultiCalendar()

    calendars = {
        'xray': {
            'xray:alpha': {
                'end': 3000,
                'local_id': 'xray:alpha',
                'start': 2000,
                'summary': 'Alpha',
            },
        },
        'yankee': {
            'yankee:bravo': {
                'end': 7000,
                'local_id': 'yankee:bravo',
                'start': 5000,
                'summary': 'Bravo',
            },
        },
        'zulu': {
            'zulu:charlie': {
                'end': 8000,
                'local_id': 'zulu:charlie',
                'start': 6000,
                'summary': 'Charlie',
            },
        },
    }
    dummycal = collections.namedtuple('_', 'events')

    with monkeypatch.context() as monkey:
        monkey.setattr('metabot.calendars.loader.get', lambda calid: dummycal(calendars[calid]))
        monkey.setattr('time.time', lambda: 1000.)
        multical.add('xray')
        multical.add('yankee')
        multical.add('zulu')

    assert multical.by_local_id == {'xray:alpha': 0, 'yankee:bravo': 1, 'zulu:charlie': 2}
    alpha, bravo, charlie = multical.ordered

    assert multical.get_event('xray:alpha') == (None, alpha, bravo)
    assert multical.get_event('yankee:bravo') == (alpha, bravo, charlie)
    assert multical.get_event('zulu:charlie') == (bravo, charlie, None)

    view = multical.view({'xray'})

    assert view.get_event('unset') == (None, None, None)
    assert view.get_event('xray:alpha') == (None, alpha, None)

    view = multical.view({'xray', 'zulu'})

    assert view.get_event('xray:alpha') == (None, alpha, charlie)
    assert view.get_event('zulu:charlie') == (alpha, charlie, None)

    assert list(multical.get_overlap(3000, 6000)) == [alpha, bravo, charlie]
    assert list(view.get_overlap(3000, 6000)) == [alpha, charlie]

    with monkeypatch.context() as monkey:
        monkey.setattr('time.time', lambda: 1000.)
        assert multical.current_index == 0
        assert view.current_index == 0
        assert view.get_event() == (None, alpha, charlie)

        monkey.setattr('time.time', lambda: 4000.)
        assert multical.current_index == 1
        assert view.current_index == 2
        assert view.get_event() == (alpha, charlie, None)

        view = multical.view({'xray'})

        assert multical.current_index == 1
        assert view.current_index is None
        assert view.get_event() == (None, None, None)

        monkey.setattr('time.time', lambda: 9000.)
        assert multical.current_index is None
        assert view.current_index is None
        assert view.get_event() == (None, None, None)
