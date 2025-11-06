"""Display recent and upcoming events."""

import ntelebot
import pytz

from metabot.util import adminui
from metabot.util import eventutil
from metabot.util import html
from metabot.util import humanize

ALIASES = ('calendar', 'event', 'events')


def modhelp(*, sections, **_):  # pylint: disable=missing-docstring
    sections['commands'].add('/events \u2013 Display recent and upcoming events')


def moddispatch(*, ctx, msg):  # pylint: disable=missing-docstring
    mgr = ctx.mgr
    modconf = mgr.bot_conf['events']

    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        if ctx.chat['type'] != 'private':
            return group(ctx, msg)
        if ctx.prefix == 'set':
            return settings(ctx, msg, modconf)
        return private(ctx, msg, modconf)

    if ctx.type == 'inline_query' and ctx.prefix.lstrip('/') in ALIASES:
        return inline(ctx)

    return False


def group(ctx, msg):
    """Handle /events in a group chat."""

    mgr = ctx.mgr
    calconf = eventutil.CalendarConf(mgr.chat_conf)
    if not calconf.calcodes or not calconf.tzinfo:
        missing = []
        if not calconf.calcodes:
            missing.append('choose one or more calendars')
        if not calconf.tzinfo:
            missing.append('set the time zone')
        return msg.add(
            "I'm not configured for this group! Ask a bot admin to go into the <b>moderator</b> "
            'module settings, group <b>%s</b>, and %s.', mgr.chat_id, humanize.list(missing))

    events = calconf.get_events(ctx.multibot)
    if not events:
        msg.add('No events in the next %s days!', calconf.days)
    else:
        url = eventutil.get_image(events[0], ctx.bot.config)
        if url:
            msg.add('photo:' + url)
        msg.add(eventutil.format_events(ctx.bot, events, calconf.tzinfo))


def private(ctx, msg, modconf):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    """Handle /events in a private chat."""

    mgr = ctx.mgr
    eventid, timezone, action, text = ctx.split(4)
    if timezone == 'admin' and mgr.user_id in ctx.bot.config['issue37']['admin']['admins']:
        return customize(ctx, msg, modconf)
    if timezone == '-':
        timezone = ''
    if ':' in eventid and timezone:
        suffix = timezone
        calcodes = eventid.split(':', 1)[0]
    else:
        suffix = '-'
        calcodes = mgr.user_conf.get('calendars')
        timezone = mgr.user_conf.get('timezone')
        if not calcodes or not timezone:
            missing = []
            if not calcodes:
                missing.append('choose one or more calendars')
            if not timezone:
                missing.append('set your time zone')
            msg.add(f'Please {humanize.list(missing)}!')
            return msg.button('Settings', '/events set')

    calendar_view = ctx.multibot.multical.view(calcodes.split())
    tzinfo = pytz.timezone(timezone)

    prevev, event, nextev = calendar_view.get_event(eventid)
    if not event:
        action = ''
        prevev, event, nextev = calendar_view.get_event()
    if not event:
        msg.add('No upcoming events!')
    else:
        eventid = event['local_id']
        rsvpconf = modconf['rsvp'][eventid][mgr.user_id]

        if action == 'going':
            rsvpconf['going'] = '+'
        elif action == 'maybe':
            rsvpconf['going'] = '?'
        elif action == 'notgoing':
            rsvpconf['going'] = None
        elif action == 'note':
            if text:
                if text.lower() in ('-', 'none', 'off'):
                    text = None
                rsvpconf['note'] = text
            else:
                msg.path('/events', 'Events')
                msg.path(eventid)
                msg.path(suffix)
                msg.path('note', 'Note')

                msg.action = 'Type your note'
                if (note := rsvpconf.get('note')):
                    msg.add('Your note is currently <code>%s</code>.', note)
                msg.add('Type your note, or type "off" to clear your existing note.')
                return

        msg.add(eventutil.format_event(ctx.bot, event, tzinfo, full=True))

        attending = []
        othernotes = []
        for otheruser, otherrsvpconf in modconf['rsvp'][eventid].items():
            userstr = mgr.user(otheruser).user_name or f'user{otheruser}'
            userstr = f'<a href="tg://user?id={otheruser}">{html.escape(userstr)}</a>'

            if (note := otherrsvpconf.get('note')):
                note = html.escape(note).replace('\n', ' ')
                userstr = f'{userstr} \u2014 {note}'
            if otherrsvpconf.get('going') == '+':
                attending.append(userstr)
            elif note:
                othernotes.append(userstr)
        if attending:
            msg.add('<b>Attending:</b>\n\u2022 ' + '\n\u2022 '.join(attending))
        if rsvpconf.get('going') == '?':
            msg.add('(I have you down as a maybe \U0001f914.)')
        if othernotes:
            msg.add('<b>Notes:</b>\n\u2022 ' + '\n\u2022 '.join(othernotes))

        base = f'/events {eventid} {suffix} '
        buttons = [None, ('Maybe \U0001f914', base + 'maybe'), None]
        if not (going := rsvpconf.get('going')):
            buttons[0] = ("I'm going \U0001f44d", base + 'going')
        elif going == '?':
            buttons[0] = ('Definitely going \U0001f44d', base + 'going')
            buttons[1] = ('Definitely not \U0001f641', base + 'notgoing')
        else:
            buttons[0] = ("I'm not going \U0001f641", base + 'notgoing')
        if not rsvpconf.get('note'):
            buttons[2] = ('Add note \U0001f4dd', base + 'note')
        else:
            buttons[2] = ('Edit note \U0001f4dd', base + 'note')
        msg.buttons(buttons)

        if mgr.user_id in ctx.bot.config['issue37']['admin']['admins']:
            msg.button('Customize', f'/events {eventid} admin')

        image = eventutil.get_image(event, ctx.bot.config, always=True)
        if ctx.edit_id:
            if not (image_message_id := ctx.meta.get('image_message_id')):
                ctx.reply_id = ctx.edit_id
                ctx.edit_id = None
            elif image != ctx.meta.get('image_url'):
                try:
                    ctx.bot.edit_message_media(chat_id=ctx.chat['id'],
                                               message_id=image_message_id,
                                               media={
                                                   'type': 'photo',
                                                   'media': image,
                                               })
                except ntelebot.errors.Unmodified:
                    pass
                ctx.meta['image_url'] = image
        if ctx.reply_id:
            image_message = ctx.bot.send_photo(chat_id=ctx.chat['id'], photo=image)
            ctx.meta['image_message_id'] = image_message['message_id']
            ctx.meta['image_url'] = image

    buttons = [None, ('Settings', '/events set'), None]
    if prevev:
        previd = prevev['local_id']
        buttons[0] = ('Prev', f'/events {previd} {suffix}')
    if suffix != '-':
        buttons[1] = ('My Events', '/events')
    elif event and event['local_id'] != calendar_view.current_local_id:
        buttons[1] = ('Current', '/events')
    if nextev:
        nextid = nextev['local_id']
        buttons[2] = ('Next', f'/events {nextid} {suffix}')
    msg.buttons(buttons)


def inline(ctx):  # pylint: disable=too-many-branches,too-many-locals
    """Handle @BOTNAME events."""

    mgr = ctx.mgr
    calcodes = mgr.user_conf.get('calendars')
    timezone = mgr.user_conf.get('timezone')
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

    calendar_view = ctx.multibot.multical.view(calcodes.split())
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

    eventid, _, field, text = ctx.split(4)

    msg.path('/events', 'Events')
    msg.path(eventid)
    msg.path('admin', 'Customize')

    _, event, _ = ctx.multibot.multical.get_event(eventid)
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

    mgr = ctx.mgr
    _, text = ctx.split(2)

    msg.path('/events', 'Events')
    msg.path('set', 'Settings')

    user_id = f'{mgr.user_id}'
    adminui.Menu(
        ('calendars', adminui.calendars, 'Which calendars do you want to see?'),
        ('timezone', adminui.timezone, 'What time zone are you in?'),
    ).handle(adminui.Frame(ctx, msg, modconf['users'], user_id, None, text))
