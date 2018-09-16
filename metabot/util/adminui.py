"""Reusable UI elements for admin functions (like /admin BOTNAME moderator and /events set)."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytz


def calendars(ctx, msg, subconf, field, text):
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
    msg.add('Select a calendar to add or remove from the list below:')
    for calcode, calendar_info in sorted(
            ctx.bot.multibot.calendars.items(), key=lambda pair: pair[1]['name']):
        if calcode not in calcodes:
            msg.button('Add %s' % calendar_info['name'], 'add %s' % calcode)
        else:
            msg.button('Remove %s' % calendar_info['name'], 'remove %s' % calcode)


def timezone(unused_ctx, msg, subconf, field, text):
    """Configure a time zone."""

    if text in pytz.common_timezones_set:
        subconf[field] = text
        return msg.add('Set timezone to <code>%s</code>.', text)

    numslashes = text.count('/')
    if text:
        numslashes += 1

    timezones = {
        tzname.replace('/', '^', numslashes).split('/', 1)[0].replace('^', '/')
        for tzname in pytz.common_timezones_set
        if tzname.startswith(text)
    }

    msg.action = 'Choose a time zone'
    msg.add('Choose a time zone:')
    for tzname in sorted(timezones):
        msg.button(tzname, tzname)
