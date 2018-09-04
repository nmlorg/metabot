"""Count down to a specific date/time."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime


def moddispatch(ctx, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in modconf:
        return countdown(ctx, modconf[ctx.command])

    return False


def countdown(ctx, timestamp):  # pylint: disable=missing-docstring
    now = datetime.datetime.utcnow()
    when = datetime.datetime.utcfromtimestamp(timestamp)
    if now > when:
        return ctx.reply_html(format_delta(now - when) + ' ago')
    return ctx.reply_html(format_delta(when - now))


def format_delta(delta):
    """Format a datetime.timedelta into "5 days, 1 hour, 13.4 seconds", etc."""

    hours = delta.seconds // (60 * 60)
    minutes = delta.seconds // 60 % 60
    seconds = delta.seconds % 60 + delta.microseconds // 10000 / 100
    message = []
    if delta.days:
        message.append(plural(delta.days, 'day', '<b>%i</b> %s'))
    if hours:
        message.append(plural(hours, 'hour', '<b>%i</b> %s'))
    if minutes:
        message.append(plural(minutes, 'minute', '<b>%i</b> %s'))
    if seconds:
        message.append(plural(seconds, 'second', '<b>%s</b> %s'))
    if message:
        return ', '.join(message)
    return '<b>NOW</b>'


def plural(num, noun, fmtstr='%s %s'):
    """Return '1 noun', '2 nouns', etc."""

    if num == 1:
        return fmtstr % (num, noun)
    return fmtstr % (num, noun + 's')


def admin(ctx, msg, modconf):
    """Handle /admin BOTNAME countdown."""

    command, _, timestamp = ctx.text.partition(' ')
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
            "Type the name of a command to add (like <code>days</code>--don't include a slash at "
            'the beginning!), or select an existing countdown to remove.')
        for command, timestamp in sorted(modconf.items()):
            msg.button('/%s (%s)' % (command, timestamp), '%s remove' % command)
        ctx.set_conversation('')
        return msg.reply(ctx)

    msg.path(command)
    msg.action = 'Type the time for /' + command
    msg.add('This is a little technical (it will be made simpler in the future), but type the unix '
            'timestamp to count down to.')
    msg.add('(Go to https://www.epochconverter.com/, fill out the section "Human date to '
            'Timestamp", then use the number listed next to "Epoch timestamp".)')
    ctx.set_conversation(command)
    return msg.reply(ctx)
