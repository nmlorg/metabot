"""Display recent and upcoming events."""

import datetime
import time
import urllib.parse

import pytz

from metabot.util import geoutil
from metabot.util import html
from metabot.util import humanize
from metabot.util import tickets


def get_group_conf(groupconf):
    """Pull calendar configuration from a raw group conf."""

    timezone = groupconf.get('timezone')
    tzinfo = timezone and pytz.timezone(timezone)
    return (groupconf.get('calendars', '').split(), tzinfo, groupconf.get('maxeventscount', 10),
            groupconf.get('maxeventsdays',
                          6), groupconf['daily'].get('hour'), groupconf['daily'].get('dow', 0))


def get_group_events(bot, calcodes, tzinfo, count, days, now=None):  # pylint: disable=too-many-arguments
    """Build a list of events for the given calendar configuration."""

    calendar_view = bot.multibot.multical.view(calcodes)
    if now is None:
        now = time.time()
    nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
    midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (midnight + datetime.timedelta(days=days + 1) - nowdt).total_seconds()
    return list(calendar_view.get_overlap(now, now + period))[:count]


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

    geo = geoutil.lookup(address, now)
    if not geo or not geo.get('forecast'):
        return
    warnings = []
    if geo['forecast']['temperatureUnit'] == 'F':
        if not 65 <= geo['forecast']['temperature'] <= 85:
            warnings.append('%s\u2109' % geo['forecast']['temperature'])
    elif geo['forecast']['temperatureUnit'] == 'C':
        if not 18 <= geo['forecast']['temperature'] <= 29:
            warnings.append('%s\u2103' % geo['forecast']['temperature'])
    short = geo['forecast']['shortForecast'].lower()
    if 'rain' in short or 'snow' in short:
        warnings.append(geo['forecast']['shortForecast'])
    return ' \u2022 '.join(warnings)


def humanize_range(start, end, tzinfo):
    """Return the range between start and end as human-friendly text."""

    return humanize.range(datetime.datetime.fromtimestamp(start, tzinfo),
                          datetime.datetime.fromtimestamp(end, tzinfo))
