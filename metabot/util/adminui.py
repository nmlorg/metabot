"""Reusable UI elements for admin functions (like /admin BOTNAME moderator and /events set)."""

import math

import pytz

from metabot.util import humanize
from metabot.util import tzutil


class Frame:  # pylint: disable=too-few-public-methods
    """The current position (and related state) within a hierarchical message."""

    def __init__(self, parent, field, desc, text):
        self.parent = parent
        self.field = field
        self.desc = desc
        self.text = text


def announcement(ctx, msg, frame):
    """Configure a daily announcement."""

    if not frame.text:
        msg.add(frame.desc)

    fieldset = (
        ('hour', integer, 'At what hour?'),
        ('dow', daysofweek, 'Which days of the week should I announce upcoming events on?'),
        ('text', freeform,
         'One or more messages (one per line) to use/cycle through for the daily announcement.'),
    )
    return fields(ctx, msg, frame, fieldset)


def bool(unused_ctx, msg, frame):  # pylint: disable=redefined-builtin
    """Configure a toggle-able setting."""

    if frame.parent.get(frame.field):
        frame.parent.pop(frame.field)
        msg.add('Disabled <code>%s</code>.', frame.field)
    else:
        frame.parent[frame.field] = True
        msg.add('Enabled <code>%s</code>.', frame.field)


def calendars(ctx, msg, frame):
    """Configure a selection of calendars."""

    action, _, target = frame.text.partition(' ')

    calcodes = set(frame.parent.get(frame.field, '').split())

    if target and target not in ctx.bot.multibot.calendars:
        msg.add('<code>%s</code> is not a calendar!', target)
    elif action == 'add' and target:
        if target in calcodes:
            msg.add('<code>%s</code> is already in your calendar view!', target)
        else:
            msg.add('Added <code>%s</code> to your calendar view.', target)
            calcodes.add(target)
    elif action == 'remove' and target:
        if target not in calcodes:
            msg.add('<code>%s</code> is not in your calendar view!', target)
        else:
            msg.add('Removed <code>%s</code> from your calendar view.', target)
            calcodes.remove(target)

    if calcodes:
        frame.parent[frame.field] = ' '.join(sorted(calcodes))
    else:
        frame.parent.pop(frame.field)

    msg.action = 'Select a calendar'
    msg.add(frame.desc)
    msg.add('Select a calendar to add or remove from the list below:')
    for calcode, calendar_info in sorted(ctx.bot.multibot.calendars.items(),
                                         key=lambda pair: pair[1]['name']):
        if calcode not in calcodes:
            msg.button('Add %s' % calendar_info['name'], 'add %s' % calcode)
        else:
            msg.button('Remove %s' % calendar_info['name'], 'remove %s' % calcode)


def daysofweek(unused_ctx, msg, frame):  # pylint: disable=too-many-branches
    """Select days of the week to enable/disable."""

    value = frame.parent.get(frame.field, 0)
    if frame.text == 'all':
        value = 0
    elif frame.text == 'none':
        value = 127
    elif frame.text.isdigit():
        value ^= 1 << int(frame.text)
    if value:
        frame.parent[frame.field] = value
    else:
        frame.parent.pop(frame.field)

    msg.action = 'Select a day of the week to toggle'
    msg.add(frame.desc)
    if value == 127:
        msg.add('All days are currently <b>disabled</b>.')
    elif not value:
        msg.add('All days are currently <b>enabled</b>.')
    else:
        days = [
            name for name, code in (('Sunday', 6), ('Monday', 0), ('Tuesday', 1), ('Wednesday', 2),
                                    ('Thursday', 3), ('Friday', 4), ('Saturday', 5))
            if not value & 1 << code
        ]
        msg.add('Enabled for %s.', humanize.list(days))

    msg.add('Select a day of the week to toggle:')
    layout = (
        (('Sunday', 6), ('Monday', 0)),
        (('Tuesday', 1), ('Wednesday', 2)),
        (('Thursday', 3), ('Friday', 4)),
        (('Saturday', 5), ('every day', -1)),
    )
    for row in layout:
        buttons = []
        for title, code in row:
            if code == -1:
                if value:
                    buttons.append(('enable ' + title, 'all'))
                else:
                    buttons.append(('disable ' + title, 'none'))
            elif value & 1 << code:
                buttons.append(('enable ' + title, '%s' % code))
            else:
                buttons.append(('disable ' + title, '%s' % code))
        msg.buttons(buttons)


def fields(ctx, msg, frame, fieldset, what='field'):
    """Present a menu of fields to edit."""

    field, _, text = frame.text.partition(' ')
    subconf = frame.parent[frame.field]
    for fieldname, uifunc, fielddesc in fieldset:
        if fieldname == field:
            msg.path(field)
            uifunc(ctx, msg, Frame(subconf, field, fielddesc, text))
            if not msg.action:
                msg.pathpop()
            break
    else:
        if field:
            msg.add("I can't set <code>%s</code>.", field)

    if not msg.action:
        msg.action = 'Choose a ' + what
        for fieldname, uifunc, fielddesc in fieldset:
            value = subconf.get(fieldname)
            if uifunc is bool:
                value = value and 'yes' or 'no'
            elif isinstance(value, dict):
                value = None
            elif value is not None:
                value = '%s' % value
                if len(value) > 10:
                    value = value[:9] + '\u2026'
            label = value and '%s (%s)' % (fieldname, value) or fieldname
            msg.button('%s \u2022 %s' % (label, fielddesc), fieldname)


def forward(ctx, msg, frame):
    """Configure the bot to forward messages from one chat to another."""

    msg.add(frame.desc)
    fieldset = (
        ('from', groupid, 'What group should messages be forwarded from?'),
        ('notify', bool, 'Should forwarded messages trigger a notification?'),
    )
    return fields(ctx, msg, frame, fieldset)


def freeform(ctx, msg, frame):  # pylint: disable=too-many-branches
    """Configure a free-form text field."""

    if ctx.document:  # pragma: no cover
        text = 'document:%s' % ctx.document
    elif ctx.photo:  # pragma: no cover
        text = 'photo:%s' % ctx.photo
    elif ctx.sticker:  # pragma: no cover
        text = 'sticker:%s' % ctx.sticker
    else:
        text = frame.text

    if text:
        if text.lower() in ('-', 'none', 'off'):
            text = ''
        if frame.parent.get(frame.field):
            if text:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.',
                        frame.field, frame.parent[frame.field], text)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', frame.field,
                        frame.parent[frame.field])
        elif text:
            msg.add('Set <code>%s</code> to <code>%s</code>.', frame.field, text)
        else:
            msg.add('Unset <code>%s</code>.', frame.field)
        if text:
            frame.parent[frame.field] = text
        else:
            frame.parent.pop(frame.field)
    else:
        msg.action = 'Type a new value for ' + frame.field
        msg.add(frame.desc)
        if frame.parent.get(frame.field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', frame.field,
                    frame.parent[frame.field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')


def groupid(ctx, msg, frame):
    """Select a group."""

    if frame.text in ctx.targetbotconf['issue37']['moderator']:
        frame.parent[frame.field] = frame.text
        msg.add('Set <code>%s</code> to <code>%s</code>.', frame.field, frame.text)
        return

    msg.action = 'Select a group'
    msg.add(frame.desc)
    msg.add('Select a group:')
    for group_id, groupconf in sorted(ctx.targetbotconf['issue37']['moderator'].items()):
        msg.button('%s (%s)' % (group_id, groupconf['title']), group_id)


def integer(unused_ctx, msg, frame):
    """Configure an integer field."""

    if frame.text:
        try:
            value = int(frame.text)
        except ValueError:
            value = None
        if frame.parent.get(frame.field) is not None:
            if value is not None:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.',
                        frame.field, frame.parent[frame.field], value)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', frame.field,
                        frame.parent[frame.field])
        elif value is not None:
            msg.add('Set <code>%s</code> to <code>%s</code>.', frame.field, value)
        else:
            msg.add('<code>%s</code> is already unset.', frame.field)
        if value is not None:
            frame.parent[frame.field] = value
        else:
            frame.parent.pop(frame.field)
    else:
        msg.action = 'Type a new value for ' + frame.field
        msg.add(frame.desc)
        if frame.parent.get(frame.field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', frame.field,
                    frame.parent[frame.field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')


def timezone(unused_ctx, msg, frame):
    """Configure a time zone."""

    if frame.text in pytz.all_timezones_set:
        frame.parent[frame.field] = frame.text
        return msg.add('Set <code>%s</code> to <code>%s</code>.', frame.field, frame.text)

    country, _, page = frame.text.partition(' ')
    country = country.upper()
    page = page.isdigit() and int(page) or 0

    timezones = [(ent.zone, ent.comment) for ent in tzutil.ZONE_TAB if ent.code == country]

    if not timezones:
        msg.action = 'Type your 2-letter country code'
        if country:
            msg.add('Unknown country code <code>%s</code>.', country)
        return msg.add('Type your 2-letter country code (like US, CA, GB, etc.).')

    pages = math.ceil(len(timezones) / 7)
    timezones = timezones[page * 7:(page + 1) * 7]

    msg.action = 'Choose a primary city'
    msg.add(frame.desc)
    msg.add('Choose a primary city:')
    for tzname, comment in timezones:
        title = tzname.rsplit('/', 1)[-1].replace('_', ' ')
        if comment:
            title = '%s (%s)' % (title, comment)
        msg.button(title, tzname)
    buttons = [None, None]
    if page:
        buttons[0] = ('Prev', '%s %i' % (country, page - 1))
    if page < pages - 1:
        buttons[1] = ('Next', '%s %i' % (country, page + 1))
    if buttons[0] or buttons[1]:
        msg.buttons(buttons)
