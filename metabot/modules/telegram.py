"""Manage the bot's Telegram state."""

from __future__ import absolute_import, division, print_function, unicode_literals


def admin(ctx, msg, modconf):
    """Handle /admin BOTNAME telegram (manage the bot's Telegram state)."""

    username = ctx.command.split()[1]
    msg.action = 'Choose an action'

    if ctx.text == 'stop':
        if not modconf['running']:
            msg.add('@%s is not currently running.', username)
        else:
            ctx.bot.multibot.stop_bot(username)
            msg.add('@%s is now offline.', username)
    elif ctx.text == 'start':
        if modconf['running']:
            msg.add('@%s is already running.', username)
        else:
            ctx.bot.multibot.run_bot(username)
            msg.add('@%s is now running.', username)

    if modconf['running']:
        msg.button('Stop bot', 'stop')
    else:
        msg.button('Start bot', 'start')
