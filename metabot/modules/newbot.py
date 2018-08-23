"""Set up new bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot

from metabot import util


def dispatch(ctx):
    """Check and dispatch relevant contexts."""

    if ctx.type not in ('message', 'callback_query'):
        return False
    callback = {
        'newbot': default,
    }.get(ctx.command)
    if not callback:
        return False

    ctx.private = True
    return callback(ctx)


def default(ctx):  # pylint: disable=missing-docstring
    msg = util.msgbuilder.MessageBuilder()
    msg.title.append('Add a bot')
    msg.action = 'Paste a bot API Token'

    token = ctx.text.partition(' ')[0]
    if not token:
        msg.add("To create a new bot, let me know your bot account's API Token. This is a code "
                'that looks like:')
        msg.add('<pre>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</pre>')
        msg.add('If you are creating a bot entirely from scratch, open a private chat with '
                '@BotFather and follow the process at '
                'https://core.telegram.org/bots#creating-a-new-bot to create a new bot account. At '
                'the end of that process, you will receive an API Token that you can paste here.')
        msg.add('Otherwise, open a private chat with @BotFather, type <code>/mybots</code>, select '
                'the bot account you want to use, select <code>API Token</code>, then copy the '
                'code and paste it here:')
        ctx.set_conversation('')
        return msg.reply(ctx)

    bot = ntelebot.bot.Bot(token)
    try:
        bot_info = bot.get_me()
    except ntelebot.errors.Unauthorized:
        msg.add(
            'Woops, Telegram told me <code>%s</code> is unauthorized, meaning the code is either '
            'incomplete or out of date. If you generated it yourself, open a private chat with '
            "@BotFather, type <code>/mybots</code>, select the bot account you're trying to use, "
            'select <code>API Token</code>, then copy the code and paste it here. If you got the '
            'code from someone else, send them these instructions (including the token I used). If '
            "the code you got from BotFather isn't working, select <code>Revoke current "
            'token</code> to generate a new one, then paste that new one here:', token)
        ctx.set_conversation('')
        return msg.reply(ctx)
    except ntelebot.errors.Error as exc:
        msg.add('Woops, while trying to use <code>%s</code> I got error %s (<code>%s</code>).',
                token, exc.error_code, exc.description)
        ctx.set_conversation('')
        return msg.reply(ctx)

    ctx.reply_html('Cool, that API Token is for <code>%s</code>. Give me another moment...',
                   bot_info['username'])

    try:
        bot.get_updates(limit=1, timeout=10)
    except ntelebot.errors.Conflict as exc:
        msg.add('Woops, it looks like this bot account is already in use. Make sure no other bot '
                'programs are running using this API Token and paste the token again, or use '
                'another one:')
        ctx.set_conversation('')
        return msg.reply(ctx)
    except ntelebot.errors.Error as exc:
        logging.exception('While polling %r:', token)
        msg.add('Woops, while trying to use <code>%s</code> I got error %s (<code>%s</code>).',
                token, exc.error_code, exc.description)
        ctx.set_conversation('')
        return msg.reply(ctx)

    username = ctx.bot.multibot.add_bot(token)
    ctx.bot.multibot.get_modconf(username, 'admin')['admins'] = [ctx.user['id']]
    ctx.bot.multibot.run_bot(username)

    msg.action = 'Configure your new bot'
    msg.add(
        'Yay, I am now running <code>%s</code> (<code>%s</code>). Open a private chat with @%s and '
        'type <code>/admin</code> to continue setup.', bot_info['username'], bot_info['first_name'],
        bot_info['username'])
    return msg.reply(ctx)
