"""Quick routine to extract ticket information from event descriptions."""

import json
import logging
import re

import ntelebot


def get_info(text):
    """Quick routine to extract ticket information from event descriptions."""

    for provider in (_brownpapertickets, _eventbrite):
        yield from provider(text)


def _brownpapertickets(text):
    events = {
        event_id for _, _, event_id in re.findall(
            '://(www.|m.|)(brownpapertickets.com|bpt.me)/event/([0-9]+)', text)
    }
    for event_id in sorted(events):
        ret = re.search(
            '>([0-9]+) tickets remaining',
            ntelebot.requests.get(f'https://m.bpt.me/event/{event_id}', timeout=10).text)
        if ret:
            remaining = int(ret.groups()[0])
        else:
            remaining = 0
        yield remaining, f'https://bpt.me/event/{event_id}'


def _eventbrite(text):
    events = {
        event_id for _, event_id in re.findall('://www.eventbrite.com/e/([^/]+-)?([0-9]+)', text)
    }
    for event_id in sorted(events):
        url = f'https://www.eventbrite.com/ajax/event/{event_id}/ticket_classes/for_sale/'
        try:
            data = ntelebot.requests.get(url,
                                         timeout=10,
                                         params={
                                             'pos': 'online',
                                         },
                                         headers={
                                             'x-requested-with': 'XMLHttpRequest',
                                         }).json()
        except json.decoder.JSONDecodeError:
            logging.exception('Decoding %s:', url)
        else:
            remaining = 0
            for ticket_class in data['ticket_classes']:
                if ticket_class['number_of_tickets_remaining']:  # If unset, this is None, not 0.
                    remaining += ticket_class['number_of_tickets_remaining']
            yield remaining, data['event_info']['vanity_url']
