"""Process natural-language messages."""

import logging
import re

import pytz

from metabot.util import eventutil


def moddispatch(*, ctx, msg):  # pylint: disable=missing-docstring
    if ctx.type == 'message' and not ctx.command:
        return process(ctx, msg)

    return False


PATTERNS = tuple(
    re.compile(f'{pattern}$') for pattern in [
        '(when|where) is( the( next)?)? (?P<event>.+?)( (at|in)( the)? (?P<location>.+?))?',
    ])


def process(ctx, msg):
    """Look for free-form text corresponding to a line in PATTERNS, and dispatch it."""

    text = ' '.join(re.split(r'\W+', ctx.text.lower())).strip()

    for pattern in PATTERNS:
        if not (ret := pattern.match(text)):
            continue
        query = ret.groupdict()
        if query['location'] is None:
            query['location'] = ''
        logging.info('Parsed: %s', ', '.join('%s=%r' % (k, v) for k, v in sorted(query.items())))
        if query.get('event'):
            return process_event(ctx, msg, query)

    return False


def process_event(ctx, msg, query):  # pylint: disable=too-many-branches,too-many-locals
    """Process queries of the form "When is the next XXX?"."""

    mgr = ctx.mgr
    if ctx.chat['type'] == 'private':
        conf = mgr.user_conf
    else:
        conf = mgr.chat_conf
    calcodes = conf.get('calendars', '').split()
    if not calcodes:
        return False
    calendar_view = ctx.multibot.multical.view(calcodes)
    timezone = pytz.timezone(conf.get('timezone', 'UTC'))

    summaries = set()
    venues = {''}
    nextev = {'local_id': None}
    while nextev:
        _, event, nextev = calendar_view.get_event(nextev['local_id'])
        if not event:
            break
        norm_summary = event['summary'].lower()
        norm_location = event['location'].lower()
        if query['event'] not in norm_summary or query['location'] not in norm_location:
            continue

        norm_venue = norm_location.split(',', 1)[0]
        if not summaries:
            reason = query['event']
            if query['location']:
                reason = f"{reason} at {query['location']}"
        elif norm_summary not in summaries:
            reason = event['summary']
            if query['location']:
                reason = f"{reason} at {query['location']}"
        elif norm_venue not in venues:
            reason = f"{query['event']} at {event['location'].split(',', 1)[0]}"
        else:
            continue

        msg.add('<i>The next %s is:</i>', reason)
        msg.add(eventutil.format_event(mgr, event, timezone, full=False))
        summaries.add(norm_summary)
        venues.add(norm_venue)
