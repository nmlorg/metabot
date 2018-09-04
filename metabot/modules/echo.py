"""Create custom commands that just return fixed messages."""

from __future__ import absolute_import, division, print_function, unicode_literals


def moddispatch(ctx, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in modconf:
        return echo(ctx, modconf[ctx.command])

    return False


def echo(ctx, message):  # pylint: disable=missing-docstring
    return ctx.reply_text(message)


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
            "Type the name of a command to add (like <code>rules</code>--don't include a slash at "
            'the beginning!), or select an existing echo to remove.')
        for command, message in sorted(modconf.items()):
            msg.button('/%s (%s)' % (command, message), '%s remove' % command)
        ctx.set_conversation('')
        return msg.reply(ctx)

    msg.path(command)
    msg.action = 'Type the message for /' + command
    msg.add('Type the text you want me to send in response to <code>/%s</code>:', command)
    ctx.set_conversation(command)
    return msg.reply(ctx)
