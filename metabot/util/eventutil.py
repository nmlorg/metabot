"""Display recent and upcoming events."""

import datetime
import logging
import time
import urllib.parse

import pytz

from metabot.util import geoutil
from metabot.util import html
from metabot.util import humanize
from metabot.util import icons
from metabot.util import tickets

# https://www.weather.gov/forecast-icons
BAD_WEATHER_KEYWORDS = {
    'blizzard', 'freezing', 'heavy', 'hurricane', 'ice', 'snow', 'tornado', 'tropical'
}


class CalendarConf:  # pylint: disable=too-few-public-methods
    """A group's calendar configuration."""

    def __init__(self, groupconf):
        self.calcodes = groupconf.get('calendars', '').split()
        self.count = groupconf.get('maxeventscount', 10)
        self.days = groupconf.get('maxeventsdays', 6)
        timezone = groupconf.get('timezone')
        self.tzinfo = timezone and pytz.timezone(timezone)

    def get_events(self, multibot, *, when=None):
        """Build lists of events for the given time (or now)."""

        return _get_events(multibot, self.calcodes, self.tzinfo, self.count, self.days, now=when)


def _get_events(multibot, calcodes, tzinfo, count, days, *, now=None):  # pylint: disable=too-many-arguments,too-many-locals
    """Build lists of events for the given calendar configuration."""

    calendar_view = multibot.multical.view(calcodes)
    if now is None:
        now = time.time()
    nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
    midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (midnight + datetime.timedelta(days=days + 1) - nowdt).total_seconds()
    return list(calendar_view.get_overlap(now, now + period))[:count]


def format_event(mgr, event, tzinfo, *, full=True, base=None, countdown=True):  # pylint: disable=too-many-arguments,too-many-locals
    """Given a metabot.calendars.base.Calendar event, build a human-friendly representation."""

    rsvpconf = mgr.bot_conf['events']['rsvp'][event['local_id']]
    attending = maybes = notes = 0
    for otherrsvpconf in rsvpconf.values():
        if (going := otherrsvpconf.get('going')) == '+':
            attending += 1
        elif going == '?':
            maybes += 1
        if otherrsvpconf.get('note'):
            notes += 1
    attending = attending and f'  \U0001f44d {attending}' or ''
    maybes = maybes and f'  \U0001f914 {maybes}' or ''
    attending += maybes
    notes = notes and '\U0001f4dd  ' or ''

    message = '<b>%s</b>%s' % (html.escape(event['summary']), attending)
    for count, url in tickets.get_info(event['description']):
        if count:
            message = '%s [<a href="%s">%i tickets remaining</a>]' % (message, url, count)
        else:
            message = '%s [<a href="%s">tickets</a>]' % (message, url)
    message = '%s\n<a href="%s">%s%s</a>' % (
        message, mgr.bot_api.encode_url('/events %s %s' % (event['local_id'], tzinfo.zone)), notes,
        humanize_range(event['start'], event['end'], tzinfo, base=base, countdown=countdown))
    if (loc := event['location']):
        location_name = loc.split(',', 1)[0]
        if (location_url := _fixurl(loc)):
            geo = None
        else:
            location_url = 'https://maps.google.com/maps?' + urllib.parse.urlencode({
                'q': loc.encode('utf-8'),
            })  # yapf: disable
            geo = format_geo(loc, event['start'])
        message = '%s @ <a href="%s">%s</a>' % (message, html.escape(location_url),
                                                html.escape(location_name))
        if geo:
            message = '%s\n\u26a0 %s' % (message, geo)
    if full and event['description']:
        message = '%s\n\n%s' % (message, html.sanitize(event['description']))
    return message


def _fixurl(loc):
    loc = loc.strip()
    if loc.startswith('http://') or loc.startswith('https://'):
        return loc
    if ' ' not in loc and '.' in loc and ('/' not in loc or (loc.index('.') < loc.index('/'))):
        return f'https://{loc}'


def format_events(mgr, events, tzinfo, *, base=None, countdown=True):
    """Prepare a message containing human-friendly representations of the given events."""

    return '\n'.join(
        format_event(mgr, event, tzinfo, full=False, base=base, countdown=countdown)
        for event in events)


def format_geo(address, now):
    """Build a string of weather exceptions for the given address as of the given time."""

    try:
        forecast = geoutil.hourlyforecast(address, now)
    except Exception:  # pylint: disable=broad-except
        logging.exception('Ignoring:')
        return
    if not forecast:
        return
    warnings = []
    if set(forecast['shortForecast'].lower().split()) & BAD_WEATHER_KEYWORDS:
        warnings.append(forecast['shortForecast'])
    if warnings:
        if forecast['temperatureUnit'] == 'F':
            warnings.append('%s\u2109' % forecast['temperature'])
        elif forecast['temperatureUnit'] == 'C':
            warnings.append('%s\u2103' % forecast['temperature'])
        return ' \u2022 '.join(warnings)


def humanize_range(start, end, tzinfo, *, base=None, countdown=True):
    """Return the range between start and end as human-friendly text."""

    startdt = datetime.datetime.fromtimestamp(start, tzinfo)
    enddt = datetime.datetime.fromtimestamp(end, tzinfo)
    text = humanize.range(startdt, enddt, base=base)
    if countdown:
        text = f'{humanize.howrecent(startdt, enddt, base=base)} {text}'
    return text


def get_image(mgr, event, *, strict=False, always=False):
    """Choose the best image for a given event and botconf."""

    eventconf = mgr.bot_conf['events']
    eventimage = eventconf['events'].get(event['local_id'])
    if eventimage:
        return eventimage
    for pattern, seriesimage in eventconf['series'].items():
        if pattern.lower() in event['summary'].lower():
            return seriesimage
    if strict:
        return
    if (image := icons.match(event['summary']) or icons.match(event['description'])):
        return image
    if always:
        return icons.match('plan day')
