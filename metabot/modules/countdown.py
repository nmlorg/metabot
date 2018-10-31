"""Count down to a specific date/time."""

from __future__ import absolute_import, division, print_function, unicode_literals

import time

from metabot.util import humanize


def modhelp(unused_ctx, modconf, sections):  # pylint: disable=missing-docstring
    now = time.time()
    for command, timestamp in modconf.items():
        if now > timestamp:
            sections['commands'].add('/%s \u2013 Count up from %s' % (command, timestamp))
        else:
            sections['commands'].add('/%s \u2013 Count down to %s' % (command, timestamp))


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in modconf:
        return countdown(msg, modconf[ctx.command])

    return False


def countdown(msg, timestamp):  # pylint: disable=missing-docstring
    now = time.time()
    if now > timestamp:
        msg.add(format_delta(now - timestamp) + ' ago')
    else:
        msg.add(format_delta(timestamp - now))


def format_delta(seconds):
    """Format a number of seconds into "5 days, 1 hour, 13.4 seconds", etc."""

    days, seconds = divmod(seconds, 60 * 60 * 24)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)
    seconds = round(seconds, 2)
    if seconds == round(seconds):
        seconds = int(seconds)
    message = []
    if days:
        message.append(humanize.plural(days, 'day', '<b>%i</b> %s'))
    if hours:
        message.append(humanize.plural(hours, 'hour', '<b>%i</b> %s'))
    if minutes:
        message.append(humanize.plural(minutes, 'minute', '<b>%i</b> %s'))
    if seconds:
        message.append(humanize.plural(seconds, 'second', '<b>%s</b> %s'))
    if message:
        return ', '.join(message)
    return '<b>NOW</b>'


def admin(ctx, msg, modconf):
    """Handle /admin BOTNAME countdown."""

    command, timestamp = ctx.split(2)
    command = command.lower()

    if command and timestamp:
        if timestamp.isdigit():
            timestamp = int(timestamp)
            if command in modconf:
                msg.add('Changed /%s from <code>%s</code> to <code>%s</code>.', command,
                        modconf[command], timestamp)
            else:
                msg.add('/%s is now counting down to <code>%s</code>.', command, timestamp)
            modconf[command] = timestamp
            command = timestamp = None
        elif timestamp == 'remove':
            if command not in modconf:
                msg.add('/%s is not currently counting down to anything.', command)
            else:
                msg.add('Removed /%s (which was counting down to <code>%s</code>).', command,
                        modconf[command])
                modconf.pop(command)
            command = timestamp = None
        else:
            msg.add("I'm not sure how to count down to <code>%s</code>!", timestamp)
            timestamp = None

    if not command:
        msg.action = 'Choose a command'
        msg.add(
            "Type the name of a command to add (like <code>days</code>\u2014don't include a slash "
            'at the beginning!), or select an existing countdown to remove.')
        for command, timestamp in sorted(modconf.items()):
            msg.button('/%s (%s)' % (command, timestamp), '%s remove' % command)
        return

    msg.path(command)
    msg.action = 'Type the time for /' + command
    msg.add('This is a little technical (it will be made simpler in the future), but type the unix '
            'timestamp to count down to.')
    msg.add('(Go to https://www.epochconverter.com/, fill out the section "Human date to '
            'Timestamp", then use the number listed next to "Epoch timestamp".)')
