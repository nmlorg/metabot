"""Display recent and upcoming events."""

import datetime
import logging
import time
import urllib.parse

import pytz

from metabot.util import geoutil
from metabot.util import html
from metabot.util import humanize
from metabot.util import tickets

# https://www.weather.gov/forecast-icons
BAD_WEATHER_KEYWORDS = {
    'blizzard', 'freezing', 'heavy', 'hurricane', 'ice', 'snow', 'tornado', 'tropical'
}


def get_group_conf(groupconf):
    """Pull calendar configuration from a raw group conf."""

    timezone = groupconf.get('timezone')
    tzinfo = timezone and pytz.timezone(timezone)
    return (groupconf.get('calendars', '').split(), tzinfo, groupconf.get('maxeventscount', 10),
            groupconf.get('maxeventsdays',
                          6), groupconf['daily'].get('hour'), groupconf['daily'].get('dow', 0))


def get_group_events(bot, calcodes, tzinfo, count, days, now=None):  # pylint: disable=too-many-arguments,too-many-locals
    """Build lists of events and weather alerts for the given calendar configuration."""

    calendar_view = bot.multibot.multical.view(calcodes)
    if now is None:
        now = time.time()
    nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
    midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (midnight + datetime.timedelta(days=days + 1) - nowdt).total_seconds()
    all_events = list(calendar_view.get_overlap(now, now + max(period, 60 * 60 * 24 * 100)))
    alerts = {}
    for event in all_events:
        if event['location']:
            try:
                alertlist = geoutil.weatheralerts(event['location'])
            except Exception:  # pylint: disable=broad-except
                logging.exception('Ignoring:')
            else:
                for alert in alertlist or ():
                    alerts[alert['id']] = alert
    end = now + period
    return ([event for event in all_events[:count] if event['start'] <= end],
            [alert for alertid, alert in sorted(alerts.items())])


def format_event(bot, event, tzinfo, full=True):
    """Given a metabot.calendars.base.Calendar event, build a human-friendly representation."""

    message = '<b>%s</b>' % event['summary']
    for count, url in tickets.get_info(event['description']):
        if count:
            message = '%s [<a href="%s">%i tickets remaining</a>]' % (message, url, count)
        else:
            message = '%s [<a href="%s">tickets</a>]' % (message, url)
    message = '%s\n<a href="%s">%s</a>' % (message,
                                           bot.encode_url('/events %s %s' %
                                                          (event['local_id'], tzinfo.zone)),
                                           humanize_range(event['start'], event['end'], tzinfo))
    if event['location']:
        location_name = event['location'].split(',', 1)[0]
        location_url = 'https://maps.google.com/maps?' + urllib.parse.urlencode({
            'q': event['location'].encode('utf-8'),
        })  # yapf: disable
        message = '%s @ <a href="%s">%s</a>' % (message, location_url, location_name)
        geo = format_geo(event['location'], event['start'])
        if geo:
            message = '%s\n\u26a0 %s' % (message, geo)
    if full and event['description']:
        message = '%s\n\n%s' % (message, html.sanitize(event['description']))
    return message


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


def humanize_range(start, end, tzinfo):
    """Return the range between start and end as human-friendly text."""

    return humanize.range(datetime.datetime.fromtimestamp(start, tzinfo),
                          datetime.datetime.fromtimestamp(end, tzinfo))
