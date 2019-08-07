"""Display recent and upcoming events."""

import datetime
import random
import time
import urllib.parse

import ntelebot
import pytz

from metabot.util import adminui
from metabot.util import html
from metabot.util import humanize
from metabot.util import pickleutil
from metabot.util import tickets

ALIASES = ('calendar', 'event', 'events')


def modhelp(unused_ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    sections['commands'].add('/events \u2013 Display recent and upcoming events')


def modinit(multibot):  # pylint: disable=missing-docstring

    def _queue():
        multibot.loop.queue.puthourly(0, _hourly, jitter=random.random() * 5)

    if multibot.conf.confdir:
        recordsfname = multibot.conf.confdir + '/daily.pickle'
        records = pickleutil.load(recordsfname) or {}
    else:
        recordsfname = None
        records = {}

    def _hourly():
        try:
            multibot.multical.poll()
            _daily_messages(multibot, records)
            if recordsfname:
                pickleutil.dump(recordsfname, records)
        finally:
            _queue()

    _queue()


def _daily_messages(multibot, records):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    now = time.time()
    for botuser, botconf in multibot.conf['bots'].items():  # pylint: disable=too-many-nested-blocks
        for groupid, groupconf in botconf['issue37']['moderator'].items():
            calcodes, tzinfo, count, days, hour, dow = _get_group_conf(groupconf)
            if not tzinfo or not isinstance(hour, int):
                continue
            # See https://github.com/nmlorg/metabot/issues/26.
            bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
            bot.multibot = multibot
            form = lambda event: format_event(bot, event, tzinfo, full=False)  # pylint: disable=cell-var-from-loop
            nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
            if nowdt.hour == hour and not dow & 1 << nowdt.weekday():
                events = _get_group_events(bot, calcodes, tzinfo, count, days, now)
                if events:
                    preambles = groupconf['daily'].get('text', '').splitlines()
                    preamble = (preambles and preambles[nowdt.toordinal() % len(preambles)] or '')
                    message = bot.send_message(chat_id=groupid,
                                               text=_format_daily_message(
                                                   preamble, list(map(form, events))),
                                               parse_mode='HTML',
                                               disable_web_page_preview=True,
                                               disable_notification=True)
                    records[botuser, groupid] = (now, [event.copy() for event in events], message)
            elif (botuser, groupid) in records:
                lastnow, lastevents, lastmessage = records[botuser, groupid]
                lastmap = {event['local_id']: event for event in lastevents}
                events = _get_group_events(bot, calcodes, tzinfo, count, days, lastnow)
                curmap = {event['local_id']: event for event in events}
                removed = [form(event) for event in lastevents if event['local_id'] not in curmap]
                added = [form(event) for event in events if event['local_id'] not in lastmap]
                updated = []
                for event in events:
                    lastevent = lastmap.get(event['local_id'])
                    if not lastevent:
                        continue
                    pieces = []
                    if event['summary'] != lastevent['summary']:
                        pieces.append((lastevent['summary'], event['summary']))
                    if event['start'] != lastevent['start'] or event['end'] != lastevent['end']:
                        pieces.append((humanize_range(lastevent['start'], lastevent['end'], tzinfo),
                                       humanize_range(event['start'], event['end'], tzinfo)))
                    if event['location'] != lastevent['location']:
                        pieces.append((lastevent['location'], event['location']))
                    curdesc = html.sanitize(event['description'], strip=True).replace('\n', ' ')
                    lastdesc = html.sanitize(lastevent['description'],
                                             strip=True).replace('\n', ' ')
                    if curdesc != lastdesc:
                        pieces.append((lastdesc, curdesc))
                    if pieces:
                        updated.append(form(event))
                        for left, right in pieces:
                            updated.append('\u2022 <i>%s</i> \u2192 <b>%s</b>' %
                                           _quick_diff(left, right))

                text = ''
                for label, edits in (('Added', added), ('Removed', removed), ('Updated', updated)):
                    if edits:
                        if text:
                            text += '\n\n'
                        text = '%s%s:\n\n%s' % (text, label, '\n'.join(edits))
                if not text:
                    continue
                message = bot.send_message(chat_id=groupid,
                                           reply_to_message_id=lastmessage['message_id'],
                                           text=text,
                                           parse_mode='HTML',
                                           disable_web_page_preview=True,
                                           disable_notification=True)

                lastnowdt = datetime.datetime.fromtimestamp(lastnow, tzinfo)
                preambles = groupconf['daily'].get('text', '').splitlines()
                preamble = preambles and preambles[lastnowdt.toordinal() % len(preambles)] or ''
                updated = 'Updated'
                groupidnum = int(groupid)
                if -1002147483647 <= groupidnum < -1000000000000:
                    updated = '<a href="https://t.me/c/%s/%s">%s</a>' % (
                        -1000000000000 - groupidnum, message['message_id'], updated)
                text = '%s\n\n[%s]' % (_format_daily_message(preamble, list(map(form,
                                                                                events))), updated)
                message = bot.edit_message_text(chat_id=groupid,
                                                message_id=lastmessage['message_id'],
                                                text=text,
                                                parse_mode='HTML',
                                                disable_web_page_preview=True)

                records[botuser, groupid] = (lastnow, [event.copy() for event in events], message)


def _quick_diff(left, right):
    i = 0
    while i < len(left) and i < len(right) and right[i] == left[i]:
        i += 1
    if i > 5:
        left = '\u2026' + left[i - 4:]
        right = '\u2026' + right[i - 4:]
    if len(left) > 30:
        left = left[:29] + '\u2026'
    if len(right) > 30:
        right = right[:29] + '\u2026'
    return left, right


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
            groupconf.get('maxeventsdays',
                          6), groupconf['daily'].get('hour'), groupconf['daily'].get('dow', 0))


def _get_group_events(bot, calcodes, tzinfo, count, days, now=None):  # pylint: disable=too-many-arguments
    calendar_view = bot.multibot.multical.view(calcodes)
    if now is None:
        now = time.time()
    nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
    midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (midnight + datetime.timedelta(days=days + 1) - nowdt).total_seconds()
    return list(calendar_view.get_overlap(now, now + period))[:count]


def group(ctx, msg):
    """Handle /events in a group chat."""

    group_id = '%s' % ctx.chat['id']
    groupconf = ctx.bot.config['issue37']['moderator'][group_id]
    calcodes, tzinfo, count, days, unused_hour, unused_dow = _get_group_conf(groupconf)
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
        msg.add('\n'.join(format_event(ctx.bot, event, tzinfo, full=False) for event in events))


def private(ctx, msg, modconf):  # pylint: disable=too-many-locals
    """Handle /events in a private chat."""

    eventid, timezone = ctx.split(2)
    if ':' in eventid and timezone:
        suffix = ' ' + timezone
        calcodes = eventid.split(':', 1)[0]
    else:
        suffix = ''
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

    prevev, event, nextev = calendar_view.get_event(eventid)
    if not event:
        prevev, event, nextev = calendar_view.get_event()
    if not event:
        msg.add('No upcoming events!')
    else:
        msg.add(format_event(ctx.bot, event, tzinfo, full=True))
    buttons = [None, ('Settings', '/events set'), None]
    if prevev:
        buttons[0] = ('Prev', '/events %s%s' % (prevev['local_id'], suffix))
    if suffix:
        buttons[1] = ('My Events', '/events')
    elif event and event['local_id'] != calendar_view.current_local_id:
        buttons[1] = ('Current', '/events')
    if nextev:
        buttons[2] = ('Next', '/events %s%s' % (nextev['local_id'], suffix))
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
    if full and event['description']:
        message = '%s\n\n%s' % (message, html.sanitize(event['description']))
    return message


def humanize_range(start, end, tzinfo):
    """Return the range between start and end as human-friendly text."""

    return humanize.range(datetime.datetime.fromtimestamp(start, tzinfo),
                          datetime.datetime.fromtimestamp(end, tzinfo))


def settings(ctx, msg, modconf):
    """Handle /events set."""

    _, text = ctx.split(2)

    msg.path('/events', 'Events')
    msg.path('set', 'Settings')

    user_id = '%s' % ctx.user['id']
    adminui.Menu(
        ('calendars', adminui.calendars, 'Which calendars do you want to see?'),
        ('timezone', adminui.timezone, 'What time zone are you in?'),
    ).handle(ctx, msg, adminui.Frame(modconf['users'], user_id, None, text))
