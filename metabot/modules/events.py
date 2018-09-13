"""Display recent and upcoming events."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import time

from metabot import util

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

ALIASES = ('calendar', 'event', 'events')


def modhelp(unused_ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    sections['commands'].add('/events \u2013 Display recent and upcoming events')


def moddispatch(ctx, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        if ctx.chat['type'] != 'private':
            return group(ctx)
        if ctx.prefix == 'set':
            return settings(ctx, modconf)
        return private(ctx, modconf)

    if ctx.type == 'inline_query' and ctx.prefix.lstrip('/') in ALIASES:
        return inline(ctx, modconf)

    return False


def group(ctx):
    """Handle /events in a group chat."""

    group_id = '%s' % ctx.chat['id']
    groupconf = ctx.bot.multibot.bots[ctx.bot.username]['moderator'][group_id]
    calcodes = groupconf.get('calendars')
    if not calcodes:
        return ctx.reply_html(
            "I'm not configured for this group! Ask a bot admin to go into the "
            '<code>moderator</code> module settings, group <code>%s</code>, and set '
            "<code>calendars</code> to this group's calendars.", group_id)

    calcodes = set(calcodes.split())
    for calcode in calcodes:
        if not ctx.bot.multibot.calendars.get(calcode):
            return ctx.reply_html(
                "Woops, I don't know how to view calendar <code>%s</code>. Ask a bot admin to go "
                'into the <code>events</code> module settings and make sure this calendar is '
                'configured!', calcode)
    calendar_view = ctx.bot.multibot.multical.view(calcodes)

    now = time.time()
    events = list(calendar_view.get_overlap(now, now + 60 * 60 * 24 * 6))
    msg = util.msgbuilder.MessageBuilder()
    if not events:
        msg.add('No upcoming events!')
    else:
        for event in events:
            msg.add(format_event(ctx, event, full=False))
    return msg.reply(ctx)


def private(ctx, modconf):
    """Handle /events in a private chat."""

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]
    calcodes = userconf.get('calendars')
    if not calcodes:
        return settings(ctx, modconf)

    calcodes = set(calcodes.split())
    for calcode in calcodes:
        if not ctx.bot.multibot.calendars.get(calcode):
            return ctx.reply_html(
                "Woops, I don't know how to view calendar <code>%s</code>. Ask a bot admin to go "
                'into the <code>events</code> module settings and make sure this calendar is '
                'configured!', calcode)
    calendar_view = ctx.bot.multibot.multical.view(calcodes)

    prevev, event, nextev = calendar_view.get_event(ctx.text)
    if not event:
        prevev, event, nextev = calendar_view.get_event()
    msg = util.msgbuilder.MessageBuilder()
    if not event:
        msg.add('No upcoming events!')
    else:
        msg.add(format_event(ctx, event, full=True))
    buttons = [None, ('Settings', '/events set'), None]
    if prevev:
        buttons[0] = ('Prev', '/events ' + prevev['local_id'])
    if event and event['local_id'] != calendar_view.current_local_id:
        buttons[1] = ('Current', '/events')
    if nextev:
        buttons[2] = ('Next', '/events ' + nextev['local_id'])
    msg.buttons(buttons)
    return msg.reply(ctx)


def inline(ctx, modconf):  # pylint: disable=too-many-branches,too-many-locals
    """Handle @BOTNAME events."""

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]
    calcodes = userconf.get('calendars')
    if not calcodes:
        return ctx.reply_inline(
            [],
            is_personal=True,
            cache_time=30,
            switch_pm_text='Setup',
            switch_pm_parameter='L2V2ZW50cw')

    calcodes = set(calcodes.split())
    for calcode in calcodes:
        if not ctx.bot.multibot.calendars.get(calcode):
            return ctx.reply_inline(
                [],
                is_personal=True,
                cache_time=30,
                switch_pm_text='Setup',
                switch_pm_parameter='L2V2ZW50cw')
    calendar_view = ctx.bot.multibot.multical.view(calcodes)

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
            subtitle = humanize_range(event['start'], event['end'])
            if event['location']:
                subtitle = '%s @ %s' % (subtitle, event['location'].split(',', 1)[0])
            if full and event['description']:
                title = u'%s \u2022 %s' % (event['summary'], subtitle)
                description = util.html.sanitize(event['description'], strip=True)
            else:
                title = event['summary']
                description = subtitle
            results.append({
                'description': description,
                'input_message_content': {
                    'disable_web_page_preview': True,
                    'message_text': format_event(ctx, event, full=full),
                    'parse_mode': 'HTML',
                },
                'id': event['local_id'],
                #'thumb_url': icon,
                'title': title,
                'type': 'article',
            })
        if not nextid:
            break
    ctx.reply_inline(
        results,
        is_personal=True,
        cache_time=30,
        switch_pm_text='Settings',
        switch_pm_parameter='L2V2ZW50cyBzZXQ')


def format_event(ctx, event, full=True):
    """Given a metabot.calendars.base.Calendar event, build a human-friendly representation."""

    url = ctx.encode_url('/events ' + event['local_id'])
    message = '<b>%s</b>\n<a href="%s">%s</a>' % (event['summary'], url,
                                                  humanize_range(event['start'], event['end']))
    if event['location']:
        location_name = event['location'].split(',', 1)[0]
        location_url = 'https://maps.google.com/maps?' + urlencode({
            'q': event['location'].encode('utf-8'),
        })  # yapf: disable
        message = '%s @ <a href="%s">%s</a>' % (message, location_url, location_name)
    if full and event['description']:
        message = '%s\n\n%s' % (message, util.html.sanitize(event['description']))
    return message


def humanize_range(start, end):
    """Return the range between start and end as human-friendly text."""

    # TODO: This uses the time zone of the system where the bot is running.
    return util.humanize.range(
        datetime.datetime.fromtimestamp(start), datetime.datetime.fromtimestamp(end))


def settings(ctx, modconf):
    """Handle /events set."""

    text = ctx.text.partition(' ')[2].lstrip()

    msg = util.msgbuilder.MessageBuilder()
    msg.path('/events', 'Events')
    msg.path('set', 'Settings')

    user_id = '%s' % ctx.user['id']
    userconf = modconf['users'][user_id]

    return util.adminui.calendars(ctx, msg, userconf, 'calendars', text)
