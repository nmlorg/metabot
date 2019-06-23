"""Quick routine to extract ticket information from event descriptions."""

import re

import requests


def get_info(text):
    """Quick routine to extract ticket information from event descriptions."""

    for provider in (_brownpapertickets,):
        for count, url in provider(text):
            yield count, url


def _brownpapertickets(text):
    events = {
        event_id for _, _, event_id in re.findall(
            '://(www.|m.|)(brownpapertickets.com|bpt.me)/event/([0-9]+)', text)
    }
    for event_id in sorted(events):
        for count in re.findall('>([0-9]+) tickets remaining',
                                requests.get('https://m.bpt.me/event/' + event_id).text):
            yield int(count), 'https://bpt.me/event/' + event_id
