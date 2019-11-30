"""Process natural-language messages."""

import logging
import re

import pytz

from metabot.util import eventutil


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring,unused-argument
    if ctx.type == 'message' and not ctx.command:
        return process(ctx, msg)

    return False


PATTERNS = ('when is( the( next)?)? (?P<event>.+?)( (at|in)( the)? (?P<location>.+?))?',)


def process(ctx, msg):
    """Look for free-form text corresponding to a line in PATTERNS, and dispatch it."""

    text = ' '.join(re.split(r'\W+', ctx.text.lower())).strip()

    for pattern in PATTERNS:
        ret = re.match(pattern + '$', text)
        if not ret:
            continue
        fields = ret.groupdict()
        logging.info('Parsed: %s', ', '.join('%s=%r' % (k, v) for k, v in sorted(fields.items())))
        if fields.get('event'):
            return process_event(ctx, msg, fields)

    return False


def process_event(ctx, msg, query):  # pylint: disable=too-many-branches,too-many-locals
    """Process queries of the form "When is the next XXX?"."""

    if ctx.chat['type'] == 'private':
        conf = ctx.bot.config['issue37']['events']['users']['%s' % ctx.user['id']]
    else:
        conf = ctx.bot.config['issue37']['moderator']['%s' % ctx.chat['id']]
    calcodes = conf.get('calendars', '').split()
    timezone = pytz.timezone(conf.get('timezone', 'UTC'))

    did_first = did_cal = did_summary = did_venue = False
    summaries = set()
    venues = set()
    local_id = None
    while not did_first or not did_cal or not did_summary or not did_venue:
        _, event, nextev = ctx.bot.multibot.multical.get_event(local_id)
        if not event:
            break
        summary = event['summary'].lower()
        location = event['location'].lower()
        if query['event'] in summary and (query.get('location') or '') in location:
            venue = location.split(',', 1)[0]
            reasons = set()
            calcode = event['local_id'].split(':', 1)[0]
            if calcode not in calcodes:
                if not did_first:
                    did_first = True
                    reasons.add(query['event'] + ' I know about')
            elif not did_first:
                did_first = did_cal = True
                reasons.add(query['event'])
            elif not did_cal:
                did_cal = True
                reasons.add('%s on the %s calendar' %
                            (query['event'], ctx.bot.multibot.calendars[calcode]['name']))
            else:
                if not did_summary and summary not in summaries:
                    did_summary = True
                    reasons.add(event['summary'])
                if not did_venue and venue not in venues:
                    did_venue = True
                    reasons.add('%s at %s' % (query['event'], event['location'].split(',', 1)[0]))

            if reasons:
                msg.add('<i>The next %s is:</i>', ' / '.join(sorted(reasons)))
                msg.add(eventutil.format_event(ctx.bot, event, timezone, full=False))
                summaries.add(summary)
                venues.add(venue)

        if not nextev:
            break
        local_id = nextev['local_id']
