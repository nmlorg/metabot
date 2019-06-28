"""Manage the bot's Telegram state."""


def admin(ctx, msg, modconf, text):
    """Handle /admin BOTNAME telegram (manage the bot's Telegram state)."""

    username = ctx.targetbotuser
    msg.action = 'Choose an action'

    if text == 'stop':
        if not modconf['running']:
            msg.add('@%s is not currently running.', username)
        else:
            ctx.bot.multibot.stop_bot(username)
            msg.add('@%s is now offline.', username)
    elif text == 'start':
        if modconf['running']:
            msg.add('@%s is already running.', username)
        else:
            ctx.bot.multibot.run_bot(username)
            msg.add('@%s is now running.', username)

    if modconf['running']:
        msg.button('Stop bot', 'stop')
    else:
        msg.button('Start bot', 'start')
