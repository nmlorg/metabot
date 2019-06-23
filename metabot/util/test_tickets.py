"""Tests for metabot.util.tickets."""

from metabot.util import tickets


def test_brownpapertickets(requests_mock):
    """Quick tests for _brownpapertickets."""

    assert list(tickets.get_info('')) == []

    requests_mock.get('https://m.bpt.me/event/12345', text='Empty')

    assert list(tickets.get_info('Event http://brownpapertickets.com/event/12345 info')) == []

    requests_mock.get('https://m.bpt.me/event/12345', text='<TD>789 tickets remaining</TD>')

    assert list(tickets.get_info('Event http://brownpapertickets.com/event/12345 info')) == [
        (789, 'https://bpt.me/event/12345'),
    ]

    assert list(
        tickets.get_info(
            'Event http://brownpapertickets.com/event/12345 info http://m.bpt.me/event/12345 dupe')
    ) == [(789, 'https://bpt.me/event/12345')]

    requests_mock.get('https://m.bpt.me/event/23456', text='<TD>987 tickets remaining</TD>')

    assert list(
        tickets.get_info(
            'Event http://brownpapertickets.com/event/12345 info http://m.bpt.me/event/23456 two')
    ) == [(789, 'https://bpt.me/event/12345'), (987, 'https://bpt.me/event/23456')]
