"""Display recent and upcoming events."""

import pytz

from metabot.util import adminui
from metabot.util import eventutil
from metabot.util import html
from metabot.util import humanize

ALIASES = ('calendar', 'event', 'events')


def modhelp(unused_ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    sections['commands'].add('/events \u2013 Display recent and upcoming events')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        if ctx.chat['type'] != 'private':
            return group(ctx, msg)
        if ctx.prefix == 'set':
            return settings(ctx, msg, modconf)
        if ctx.prefix == 'admin':
            return customize(ctx, msg, modconf)
        return private(ctx, msg, modconf)

    if ctx.type == 'inline_query' and ctx.prefix.lstrip('/') in ALIASES:
        return inline(ctx, modconf)

    return False


def group(ctx, msg):
    """Handle /events in a group chat."""

    group_id = f"{ctx.chat['id']}"
    calconf = eventutil.CalendarConf(ctx.bot.config['issue37']['moderator'][group_id])
    if not calconf.calcodes or not calconf.tzinfo:
        missing = []
        if not calconf.calcodes:
            missing.append('choose one or more calendars')
        if not calconf.tzinfo:
            missing.append('set the time zone')
        return msg.add(
            "I'm not configured for this group! Ask a bot admin to go into the <b>moderator</b> "
            'module settings, group <b>%s</b>, and %s.', group_id, humanize.list(missing))

    events = calconf.get_events(ctx.bot)
    if not events:
        msg.add('No events in the next %s days!', calconf.days)
    else:
        url = eventutil.get_image(events[0], ctx.bot.config)
        if url:
            msg.add('photo:' + url)
        msg.add(eventutil.format_events(ctx.bot, events, calconf.tzinfo))


def private(ctx, msg, modconf):  # pylint: disable=too-many-branches,too-many-locals
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
            msg.add(f'Please {humanize.list(missing)}!')
            return msg.button('Settings', '/events set')

    calendar_view = ctx.bot.multibot.multical.view(calcodes.split())
    tzinfo = pytz.timezone(timezone)

    prevev, event, nextev = calendar_view.get_event(eventid)
    if not event:
        prevev, event, nextev = calendar_view.get_event()
    if not event:
        msg.add('No upcoming events!')
    else:
        msg.add(eventutil.format_event(ctx.bot, event, tzinfo, full=True))
        eventid = event['local_id']

        if ctx.user['id'] in ctx.bot.config['issue37']['admin']['admins']:
            msg.button('Customize', f'/events admin {eventid}')

    buttons = [None, ('Settings', '/events set'), None]
    if prevev:
        previd = prevev['local_id']
        buttons[0] = ('Prev', f'/events {previd}{suffix}')
    if suffix:
        buttons[1] = ('My Events', '/events')
    elif event and event['local_id'] != calendar_view.current_local_id:
        buttons[1] = ('Current', '/events')
    if nextev:
        nextid = nextev['local_id']
        buttons[2] = ('Next', f'/events {nextid}{suffix}')
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
                                switch_pm_text=f'Click to {humanize.list(missing)}!',
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
            subtitle = eventutil.humanize_range(event['start'], event['end'], tzinfo)
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
                    'message_text': eventutil.format_event(ctx.bot, event, tzinfo, full=full),
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


def customize(ctx, msg, modconf):
    """Handle /events admin."""

    _, eventid, field, text = ctx.split(4)

    msg.path('/events', 'Events')
    msg.path('admin', 'Customize')
    msg.path(eventid)

    _, event, _ = ctx.bot.multibot.multical.get_event(eventid)
    if not event:
        return msg.add('Unknown event!')

    frame = adminui.Frame(ctx, msg, modconf, 'events', None, field)
    menu = adminui.Menu(
        ('event', 'event', 'What banner image should be used for this specific event?'),
        ('series', 'series', 'What banner image should be used for events with this title?'),
    )
    _, handler = menu.select(frame)
    if handler == 'event':
        msg.path('event')
        frame = adminui.Frame(ctx, msg, modconf['events'], eventid, None, text)
        adminui.image(frame)
    elif handler == 'series':
        msg.path('series')
        frame = adminui.Frame(ctx, msg, modconf['series'], event['summary'], None, text)
        adminui.image(frame)
    else:
        menu.display(frame)


def settings(ctx, msg, modconf):
    """Handle /events set."""

    _, text = ctx.split(2)

    msg.path('/events', 'Events')
    msg.path('set', 'Settings')

    user_id = '%s' % ctx.user['id']
    adminui.Menu(
        ('calendars', adminui.calendars, 'Which calendars do you want to see?'),
        ('timezone', adminui.timezone, 'What time zone are you in?'),
    ).handle(adminui.Frame(ctx, msg, modconf['users'], user_id, None, text))
