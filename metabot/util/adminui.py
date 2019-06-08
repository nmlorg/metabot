"""Reusable UI elements for admin functions (like /admin BOTNAME moderator and /events set)."""

import builtins
import math

import pytz

from metabot.util import humanize
from metabot.util import tzutil


def bool(unused_ctx, msg, subconf, field, unused_desc, unused_text):  # pylint: disable=too-many-arguments,redefined-builtin
    """Configure a toggle-able setting."""

    subconf[field] = not subconf[field]
    msg.add('Set <code>%s</code> to <code>%s</code>.', field, subconf[field])


def calendars(ctx, msg, subconf, field, desc, text):  # pylint: disable=too-many-arguments
    """Configure a selection of calendars."""

    action, _, target = text.partition(' ')

    calcodes = set(subconf.get(field, '').split())

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
        subconf[field] = ' '.join(sorted(calcodes))
    else:
        subconf.pop(field)

    msg.action = 'Select a calendar'
    msg.add(desc)
    msg.add('Select a calendar to add or remove from the list below:')
    for calcode, calendar_info in sorted(ctx.bot.multibot.calendars.items(),
                                         key=lambda pair: pair[1]['name']):
        if calcode not in calcodes:
            msg.button('Add %s' % calendar_info['name'], 'add %s' % calcode)
        else:
            msg.button('Remove %s' % calendar_info['name'], 'remove %s' % calcode)


def daysofweek(unused_ctx, msg, subconf, field, desc, text):  # pylint: disable=too-many-arguments,too-many-branches
    """Select days of the week to enable/disable."""

    value = subconf.get(field, 0)
    if text == 'all':
        value = 0
    elif text == 'none':
        value = 127
    elif text.isdigit():
        value ^= 1 << int(text)
    if value:
        subconf[field] = value
    else:
        subconf.pop(field, None)

    msg.action = 'Select a day of the week to toggle'
    msg.add(desc)
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


def fields(ctx, msg, subconf, fieldset, field, text):  # pylint: disable=too-many-arguments
    """Present a menu of fields to edit."""

    for fieldname, uifunc, fielddesc in fieldset:
        if fieldname == field:
            uifunc(ctx, msg, subconf, field, fielddesc, text)
            break
    else:
        if field:
            msg.add("I can't set <code>%s</code>.", field)

    if msg.action:
        msg.path(field)
    else:
        msg.action = 'Choose a field'
        for fieldname, unused_uifunc, fielddesc in fieldset:
            value = subconf.get(fieldname)
            if isinstance(value, builtins.bool):
                value = value and 'yes' or 'no'
            elif value is not None:
                value = '%s' % value
                if len(value) > 10:
                    value = value[:9] + '\u2026'
            label = value and '%s (%s)' % (fieldname, value) or fieldname
            msg.button('%s \u2022 %s' % (label, fielddesc), fieldname)


def freeform(unused_ctx, msg, subconf, field, desc, text):
    """Configure a free-form text field."""

    if text:
        if text.lower() in ('-', 'none', 'off'):
            text = ''
        if subconf.get(field):
            if text:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.', field,
                        subconf[field], text)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', field, subconf[field])
        elif text:
            msg.add('Set <code>%s</code> to <code>%s</code>.', field, text)
        else:
            msg.add('Unset <code>%s</code>.', field)
        if text:
            subconf[field] = text
        else:
            subconf.pop(field)
    else:
        msg.action = 'Type a new value for ' + field
        msg.add(desc)
        if subconf.get(field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', field, subconf[field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')


def integer(unused_ctx, msg, subconf, field, desc, text):
    """Configure an integer field."""

    if text:
        if text.isdigit():
            value = int(text)
        else:
            value = None
        if subconf.get(field):
            if value is not None:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.', field,
                        subconf[field], text)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', field, subconf[field])
        elif value is not None:
            msg.add('Set <code>%s</code> to <code>%s</code>.', field, value)
        else:
            msg.add('Unset <code>%s</code>.', field)
        if value is not None:
            subconf[field] = value
        else:
            subconf.pop(field)
    else:
        msg.action = 'Type a new value for ' + field
        msg.add(desc)
        if subconf.get(field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', field, subconf[field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')


def timezone(unused_ctx, msg, subconf, field, desc, text):  # pylint: disable=too-many-arguments
    """Configure a time zone."""

    if text in pytz.all_timezones_set:
        subconf[field] = text
        return msg.add('Set timezone to <code>%s</code>.', text)

    country, _, page = text.partition(' ')
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
    msg.add(desc)
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
