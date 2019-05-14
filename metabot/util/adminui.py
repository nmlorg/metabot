"""Reusable UI elements for admin functions (like /admin BOTNAME moderator and /events set)."""

from __future__ import absolute_import, division, print_function, unicode_literals

import math

import pytz


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
            msg.button('%s \u2022 %s' % (fieldname, fielddesc), fieldname)


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


def timezone(ctx, msg, subconf, field, desc, text):  # pylint: disable=too-many-arguments
    """Configure a time zone."""

    text, _, page = text.partition(' ')
    if text == '-':
        text = ''
    page = page.isdigit() and int(page) or 0

    if text in pytz.common_timezones_set:
        subconf[field] = text
        return msg.add('Set timezone to <code>%s</code>.', text)

    timezones = ()
    if ctx.user.get('language_code', '').count('-') == 1:
        country = ctx.user['language_code'].split('-')[1].upper()
        if country == 'US':
            timezones = {tzname for tzname in pytz.common_timezones if tzname.startswith('US/')}
        elif country == 'CA':
            timezones = {tzname for tzname in pytz.common_timezones if tzname.startswith('Canada/')}
        else:
            timezones = pytz.country_timezones.get(country)

    if not timezones:
        numslashes = text.count('/')
        if text:
            numslashes += 1

        timezones = {
            tzname.replace('/', '^', numslashes).split('/', 1)[0].replace('^', '/')
            for tzname in pytz.common_timezones_set
            if tzname.startswith(text)
        }

    pages = math.ceil(len(timezones) / 7)
    timezones = sorted(timezones)[page * 7:(page + 1) * 7]

    msg.action = 'Choose a time zone'
    msg.add(desc)
    msg.add('Choose a time zone:')
    for tzname in timezones:
        msg.button(tzname, tzname)
    if page or page < pages - 1:
        buttons = [None, None]
        if page:
            buttons[0] = ('Prev', '%s %i' % (text or '-', page - 1))
        if page < pages - 1:
            buttons[1] = ('Next', '%s %i' % (text or '-', page + 1))
        msg.buttons(buttons)
