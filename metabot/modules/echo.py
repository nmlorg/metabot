"""Create custom commands that just return fixed messages."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot import util


def modhelp(unused_ctx, modconf, sections):  # pylint: disable=missing-docstring
    for command, message in modconf.items():
        if len(message) > 30:
            message = message[:29] + '\u2026'
        sections['commands'].add('/%s \u2013 "%s"' % (command, message))


def moddispatch(ctx, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in modconf:
        return echo(ctx, modconf[ctx.command])

    return False


def echo(ctx, message):  # pylint: disable=missing-docstring
    msg = util.msgbuilder.MessageBuilder()
    lines = message.splitlines()
    page = ctx.text.isdigit() and int(ctx.text) or 1
    for line in lines[:page]:
        msg.add('%s', line)
    if page < len(lines):
        ctx.private = True
        msg.button('More (%i/%i)' % (page, len(lines)), '/%s %i' % (ctx.command, page + 1))
    return msg.reply(ctx)


def admin(ctx, msg, modconf):
    """Handle /admin BOTNAME echo."""

    command, _, message = ctx.text.partition(' ')
    command = command.lower()

    if command and message:
        if message == 'remove':
            if command not in modconf:
                msg.add('/%s is not echoing anything.', command)
            else:
                msg.add('Removed /%s (<code>%s</code>).', command, modconf[command])
                modconf.pop(command)
            command = message = None
        else:
            if command in modconf:
                msg.add('Changed /%s from <code>%s</code> to <code>%s</code>.', command,
                        modconf[command], message)
            else:
                msg.add('/%s now echoes <code>%s</code>.', command, message)
            modconf[command] = message
            command = message = None

    if not command:
        msg.action = 'Choose a command'
        msg.add(
            "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash "
            'at the beginning!), or select an existing echo to remove.')
        for command, message in sorted(modconf.items()):
            msg.button('/%s (%s)' % (command, message), '%s remove' % command)
        ctx.set_conversation('')
        return msg.reply(ctx)

    msg.path(command)
    msg.action = 'Type the message for /' + command
    msg.add('Type the text you want me to send in response to <code>/%s</code>:', command)
    ctx.set_conversation(command)
    return msg.reply(ctx)
