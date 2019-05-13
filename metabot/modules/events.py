"""Display recent and upcoming events."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import random
import time

import ntelebot
import pytz

from metabot.util import adminui
from metabot.util import html
from metabot.util import humanize

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

ALIASES = ('calendar', 'event', 'events')


def modhelp(unused_ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    sections['commands'].add('/events \u2013 Display recent and upcoming events')


def modinit(multibot):  # pylint: disable=missing-docstring

    def _queue():
        multibot.loop.queue.puthourly(0, _hourly, jitter=random.random() * 5)

    def _hourly():
        multibot.multical.poll()
        for botconf in multibot.conf['bots'].values():
            for groupid, groupconf in botconf['issue37']['moderator'].items():
                calcodes, tzinfo, count, days, daily = _get_group_conf(groupconf)
                if tzinfo and isinstance(daily, int):
                    now = datetime.datetime.now(tzinfo)
                    if now.hour == daily:
                        # See https://github.com/nmlorg/metabot/issues/26.
                        bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
                        bot.multibot = multibot
                        events = _get_group_events(bot, calcodes, tzinfo, count, days)
                        if events:
                            preambles = groupconf.get('dailytext', '').splitlines()
                            preamble = (preambles and preambles[now.toordinal() % len(preambles)] or
                                        '')
                            bot.send_message(chat_id=groupid,
                                             text=_format_daily_message(preamble, events),
                                             parse_mode='HTML',
                                             disable_web_page_preview=True,
                                             disable_notification=True)
        _queue()

    _queue()


def _format_daily_message(preamble, events):
    if len(events) == 1:
        text = "There's an event coming up:"
    elif len(events) == 2:
        text = 'There are a couple events coming up:'
    elif len(events) == 3:
        text = 'There are a few events coming up:'
    else:
        text = 'There are a bunch of events coming up:'
    if preamble and preamble.endswith(':') and 'events' in preamble.lower():
        text = preamble
    elif preamble:
        if preamble[-1] in ('.', '?', '!'):
            preamble += ' '
        else:
            preamble += ' \u2022 '
        text = text[0].lower() + text[1:]
        if 'event' in preamble.lower():
            text = 'Speaking of which, ' + text
        else:
            text = 'Also, ' + text
        text = preamble + text
    return '%s\n\n%s' % (text, '\n'.join(events))


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        if ctx.chat['type'] != 'private':
            return group(ctx, msg)
        if ctx.prefix == 'set':
            return settings(ctx, msg, modconf)
        return private(ctx, msg, modconf)

    if ctx.type == 'inline_query' and ctx.prefix.lstrip('/') in ALIASES:
        return inline(ctx, modconf)

    return False


def _get_group_conf(groupconf):
    timezone = groupconf.get('timezone')
    tzinfo = timezone and pytz.timezone(timezone)
    return (groupconf.get('calendars', '').split(), tzinfo, groupconf.get('maxeventscount', 10),
            groupconf.get('maxeventsdays', 6), groupconf.get('daily'))


def _get_group_events(bot, calcodes, tzinfo, count, days):
    calendar_view = bot.multibot.multical.view(calcodes)
    now = time.time()
    nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
    midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (midnight + datetime.timedelta(days=days + 1) - nowdt).total_seconds()
    return [
        format_event(bot, event, tzinfo, full=False)
        for event in list(calendar_view.get_overlap(now, now + period))[:count]
    ]


def group(ctx, msg):
    """Handle /events in a group chat."""

    group_id = '%s' % ctx.chat['id']
    groupconf = ctx.bot.multibot.conf['bots'][ctx.bot.username]['issue37']['moderator'][group_id]
    calcodes, tzinfo, count, days, unused_daily = _get_group_conf(groupconf)
    if not calcodes or not tzinfo:
        missing = []
        if not calcodes:
            missing.append('choose one or more calendars')
        if not tzinfo:
            missing.append('set the time zone')
        return msg.add(
            "I'm not configured for this group! Ask a bot admin to go into the <b>moderator</b> "
            'module settings, group <b>%s</b>, and %s.', group_id, humanize.list(missing))

    events = _get_group_events(ctx.bot, calcodes, tzinfo, count, days)
    if not events:
        msg.add('No events in the next %s days!', days)
    else:
        msg.add('\n'.join(events))


def private(ctx, msg, modconf):
    """Handle /events in a private chat."""

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]
    calcodes = userconf.get('calendars')
    timezone = userconf.get('timezone')
    if not calcodes or not timezone:
        missing = []
        if not calcodes:
            missing.append('choose one or more calendars')
        if not timezone:
            missing.append('set your time zone')
        msg.add('Please %s!', humanize.list(missing))
        return msg.button('Settings', '/events set')

    calendar_view = ctx.bot.multibot.multical.view(calcodes.split())
    tzinfo = pytz.timezone(timezone)

    prevev, event, nextev = calendar_view.get_event(ctx.text)
    if not event:
        prevev, event, nextev = calendar_view.get_event()
    if not event:
        msg.add('No upcoming events!')
    else:
        msg.add(format_event(ctx.bot, event, tzinfo, full=True))
    buttons = [None, ('Settings', '/events set'), None]
    if prevev:
        buttons[0] = ('Prev', '/events ' + prevev['local_id'])
    if event and event['local_id'] != calendar_view.current_local_id:
        buttons[1] = ('Current', '/events')
    if nextev:
        buttons[2] = ('Next', '/events ' + nextev['local_id'])
    msg.buttons(buttons)


def inline(ctx, modconf):  # pylint: disable=too-many-branches,too-many-locals
    """Handle @BOTNAME events."""

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]
    calcodes = userconf.get('calendars')
    timezone = userconf.get('timezone')
    if not calcodes or not timezone:
        missing = []
        if not calcodes:
            missing.append('choose one or more calendars')
        if not timezone:
            missing.append('set your time zone')
        return ctx.reply_inline([],
                                is_personal=True,
                                cache_time=30,
                                switch_pm_text='Click to %s!' % humanize.list(missing),
                                switch_pm_parameter='L2V2ZW50cw')

    calendar_view = ctx.bot.multibot.multical.view(calcodes.split())
    tzinfo = pytz.timezone(timezone)

    terms = ctx.text.lower().split()[1:]
    full = False
    if terms and terms[0].lower() == 'full':
        terms.pop(0)
        full = True
    nextid = None
    results = []
    while len(results) < 25:
        _, event, nextev = calendar_view.get_event(nextid)
        nextid = nextev and nextev['local_id']
        if not event:
            break
        if full:
            text = ('%s %s' % (event['summary'], event['description'])).lower()
        else:
            text = event['summary'].lower()
        for term in terms:
            if term not in text:
                break
        else:
            subtitle = humanize_range(event['start'], event['end'], tzinfo)
            if event['location']:
                subtitle = '%s @ %s' % (subtitle, event['location'].split(',', 1)[0])
            if full and event['description']:
                title = '%s \u2022 %s' % (event['summary'], subtitle)
                description = html.sanitize(event['description'], strip=True)
            else:
                title = event['summary']
                description = subtitle
            results.append({
                'description': description,
                'input_message_content': {
                    'disable_web_page_preview': True,
                    'message_text': format_event(ctx.bot, event, tzinfo, full=full),
                    'parse_mode': 'HTML',
                },
                'id': event['local_id'],
                #'thumb_url': icon,
                'title': title,
                'type': 'article',
            })
        if not nextid:
            break
    ctx.reply_inline(results,
                     is_personal=True,
                     cache_time=30,
                     switch_pm_text='Settings',
                     switch_pm_parameter='L2V2ZW50cyBzZXQ')


def format_event(bot, event, tzinfo, full=True):
    """Given a metabot.calendars.base.Calendar event, build a human-friendly representation."""

    url = bot.encode_url('/events ' + event['local_id'])
    message = '<b>%s</b>\n<a href="%s">%s</a>' % (
        event['summary'], url, humanize_range(event['start'], event['end'], tzinfo))
    if event['location']:
        location_name = event['location'].split(',', 1)[0]
        location_url = 'https://maps.google.com/maps?' + urlencode({
            'q': event['location'].encode('utf-8'),
        })  # yapf: disable
        message = '%s @ <a href="%s">%s</a>' % (message, location_url, location_name)
    if full and event['description']:
        message = '%s\n\n%s' % (message, html.sanitize(event['description']))
    return message


def humanize_range(start, end, tzinfo):
    """Return the range between start and end as human-friendly text."""

    return humanize.range(datetime.datetime.fromtimestamp(start, tzinfo),
                          datetime.datetime.fromtimestamp(end, tzinfo))


def settings(ctx, msg, modconf):
    """Handle /events set."""

    _, field, text = ctx.split(3)

    msg.path('/events', 'Events')
    msg.path('set', 'Settings')

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]
    fields = (
        ('calendars', adminui.calendars, 'Which calendars do you want to see?'),
        ('timezone', adminui.timezone, 'What time zone are you in?'),
    )
    return adminui.fields(ctx, msg, userconf, fields, field, text)
