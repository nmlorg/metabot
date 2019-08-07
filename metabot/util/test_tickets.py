"""Tests for metabot.util.tickets."""

from metabot.util import tickets


def test_brownpapertickets(requests_mock):
    """Quick tests for _brownpapertickets."""

    assert list(tickets.get_info('')) == []

    requests_mock.get('https://m.bpt.me/event/12345', text='Empty')

    assert list(tickets.get_info('Event http://brownpapertickets.com/event/12345 info')) == [
        (0, 'https://bpt.me/event/12345'),
    ]

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


def test_eventbrite(requests_mock):
    """Quick tests for _eventbrite."""

    assert list(tickets.get_info('')) == []

    requests_mock.get('https://www.eventbrite.com/ajax/event/12345/ticket_classes/for_sale/',
                      text='Empty')

    assert list(
        tickets.get_info(
            'Event https://www.eventbrite.com/e/my-cool-event-tickets-12345 info')) == []

    requests_mock.get(
        'https://www.eventbrite.com/ajax/event/12345/ticket_classes/for_sale/',
        json={
            'event_info': {
                'vanity_url': 'https://my-cool_event.eventbrite.com',
                'status_is_sold_out': False,
                'canonical_url': 'https://www.eventbrite.com/e/my-cool-event-tickets-12345',
            },
            'ticket_classes': [{
                'number_of_tickets_remaining': None,
            }],
        })

    assert list(
        tickets.get_info(
            'Event https://www.eventbrite.com/e/my-cool-event-tickets-12345 info')) == [
                (0, 'https://my-cool_event.eventbrite.com'),
            ]

    requests_mock.get(
        'https://www.eventbrite.com/ajax/event/12345/ticket_classes/for_sale/',
        json={
            'event_info': {
                'vanity_url': 'https://my-cool_event.eventbrite.com',
                'status_is_sold_out': False,
                'canonical_url': 'https://www.eventbrite.com/e/my-cool-event-tickets-12345',
            },
            'ticket_classes': [{
                'number_of_tickets_remaining': 789,
            }],
        })

    assert list(
        tickets.get_info(
            'Event https://www.eventbrite.com/e/my-cool-event-tickets-12345 info')) == [
                (789, 'https://my-cool_event.eventbrite.com'),
            ]
