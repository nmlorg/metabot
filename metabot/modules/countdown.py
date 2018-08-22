"""Count down to a specific date/time."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime


def dispatch(ctx):
    """Check and dispatch relevant contexts."""

    if ctx.type not in ('message', 'callback_query'):
        return False

    mod_config = ctx.bot.get_modconf('countdown')
    for command, timestamp in mod_config.items():
        if command == ctx.command:
            return countdown(ctx, timestamp)

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
