"""Set up new bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot


def default(ctx):  # pylint: disable=missing-docstring
    token = ctx.text.partition(' ')[0]
    if not token:
        message = [
            'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>',
            '',
            ("To create a new bot, let me know your bot account's API Token. This is a code that "
             'looks like:'),
            '',
            '<pre>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</pre>',
            '',
            ('If you are creating a bot entirely from scratch, open a private chat with @BotFather '
             'and follow the process at https://core.telegram.org/bots#creating-a-new-bot to '
             'create a new bot account. At the end of that process, you will receive an API Token '
             'that you can paste here.'),
            '',
            ('Otherwise, open a private chat with @BotFather, type <code>/mybots</code>, select '
             'the bot account you want to use, select <code>API Token</code>, then copy the code '
             'and paste it here:'),
        ]
        ctx.set_conversation('')
        return ctx.reply_html('\n'.join(message), disable_web_page_preview=True)

    bot = ntelebot.bot.Bot(token)
    try:
        bot_info = bot.get_me()
    except ntelebot.errors.Unauthorized:
        ctx.set_conversation('')
        return ctx.reply_html(
            'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
            '\n'
            'Woops, Telegram told me <code>%s</code> is unauthorized, meaning the code is either '
            'incomplete or out of date. If you generated it yourself, open a private chat with '
            "@BotFather, type <code>/mybots</code>, select the bot account you're trying to use, "
            'select <code>API Token</code>, then copy the code and paste it here. If you got the '
            'code from someone else, send them these instructions (including the token I used). If '
            "the code you got from BotFather isn't working, select <code>Revoke current "
            'token</code> to generate a new one, then paste that new one here:', token)
    except ntelebot.errors.Error as exc:
        ctx.set_conversation('')
        return ctx.reply_html(
            'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
            '\n'
            'Woops, while trying to use <code>%s</code> I got error %i (<code>%s</code>).', token,
            exc.error_code, exc.description)

    ctx.reply_html('Cool, that API Token is for <code>%s</code>. Give me another moment...',
                   bot_info['username'])

    try:
        bot.get_updates(limit=1, timeout=10)
    except ntelebot.errors.Conflict as exc:
        ctx.set_conversation('')
        return ctx.reply_html(
            'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
            '\n'
            'Woops, it looks like this bot account is already in use. Make sure no other bot '
            'programs are running using this API Token and paste the token again, or use another '
            'one:')
    except ntelebot.errors.Error as exc:
        logging.exception('While polling %r:', token)
        ctx.set_conversation('')
        return ctx.reply_html(
            'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
            '\n'
            'Woops, while trying to use <code>%s</code> I got error %i (<code>%s</code>).', token,
            exc.error_code, exc.description)

    username = ctx.bot.multibot.add_bot(token)
    ctx.bot.multibot.enable_module(username, 'admin')
    ctx.bot.multibot.bots[username]['modules']['admin']['admins'] = [ctx.user['id']]
    ctx.bot.multibot.run_bot(username)

    ctx.reply_html(
        'Bot Admin \u203a Add a bot: <b>Configure your new bot</b>\n'
        '\n'
        'Yay, I am now running <code>%s</code> (<code>%s</code>). Open a private chat with @%s and '
        'type <code>/admin</code> to continue setup.', bot_info['username'], bot_info['first_name'],
        bot_info['username'])
