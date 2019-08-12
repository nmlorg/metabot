"""Count down to a specific date/time."""

import time

from metabot.util import adminui
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
    msg.add(format_delta(timestamp - time.time()))


def format_delta(seconds):
    """Format a number of seconds into "5 days, 1 hour, 13.4 seconds", etc."""

    if seconds < 0:
        suffix = ' ago'
        seconds = -seconds
    else:
        suffix = ''
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
        return ', '.join(message) + suffix
    return '<b>NOW</b>'


def admin(frame):
    """Handle /admin BOTNAME countdown."""

    msg = frame.msg
    menu = adminui.Menu()
    for command in frame.value:
        menu.add(command)
    menu.add(None)
    newframe, handler = menu.select(frame)
    if handler:
        if newframe.text.isdigit():
            adminui.set_log(newframe, int(newframe.text))
        elif newframe.text.lower() in ('-', 'none', 'off', 'remove'):
            adminui.set_log(newframe, None)
        else:
            if newframe.text:
                msg.add("I'm not sure how to count down to <code>%s</code>!", newframe.text)

            msg.path(newframe.field)
            msg.action = 'Type the time for /' + newframe.field
            msg.add('This is a little technical (it will be made simpler in the future), but type '
                    'the unix timestamp to count down to.')
            msg.add('(Go to https://www.epochconverter.com/, fill out the section "Human date to '
                    'Timestamp", then use the number listed next to "Epoch timestamp".)')
            if newframe.value:
                msg.add('To remove /%s (which is counting to %s), type "off".', newframe.field,
                        newframe.value)
            return

    msg.action = 'Choose a command'
    msg.add("Type the name of a command to add (like <code>days</code>\u2014don't include a slash "
            'at the beginning!), or select an existing countdown to remove.')
    # See https://github.com/nmlorg/metabot/issues/65.
    menu = adminui.Menu()
    for command in frame.value:
        menu.add(command)
    menu.display(frame, what='command')
