"""Tests for metabot.modules.newbot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import ntelebot
import pytest

from metabot.modules import newbot


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(newbot)


# pylint: disable=line-too-long


def test_default(conversation):  # pylint: disable=redefined-outer-name
    """Verify the bot's /newbot command."""

    assert conversation.message('/notnewbot') == ''

    assert conversation.message('/newbot') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Paste a bot API Token</b>

To create a new bot, let me know your bot account's API Token. This is a code that looks like:

<pre>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</pre>

If you are creating a bot entirely from scratch, open a private chat with @BotFather and follow the process at https://core.telegram.org/bots#creating-a-new-bot to create a new bot account. At the end of that process, you will receive an API Token that you can paste here.

Otherwise, open a private chat with @BotFather, type <code>/mybots</code>, select the bot account you want to use, select <code>API Token</code>, then copy the code and paste it here:
"""

    assert conversation.message('bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Paste a bot API Token</b>

Oops, <code>bogus</code> doesn't look like an API Token.

To create a new bot, let me know your bot account's API Token. This is a code that looks like:

<pre>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</pre>

If you are creating a bot entirely from scratch, open a private chat with @BotFather and follow the process at https://core.telegram.org/bots#creating-a-new-bot to create a new bot account. At the end of that process, you will receive an API Token that you can paste here.

Otherwise, open a private chat with @BotFather, type <code>/mybots</code>, select the bot account you want to use, select <code>API Token</code>, then copy the code and paste it here:
"""

    ntelebot.bot.Bot('1234:invalid').getme.respond(json={
        'description': 'Unauthorized',
        'error_code': 401,
        'ok': False,
    })

    assert conversation.message('1234:invalid') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Paste a bot API Token</b>

Woops, Telegram told me <code>1234:invalid</code> is unauthorized, meaning the code is either incomplete or out of date. If you generated it yourself, open a private chat with @BotFather, type <code>/mybots</code>, select the bot account you're trying to use, select <code>API Token</code>, then copy the code and paste it here. If you got the code from someone else, send them these instructions (including the token I used). If the code you got from BotFather isn't working, select <code>Revoke current token</code> to generate a new one, then paste that new one here:
"""

    mockbot = ntelebot.bot.Bot('1234:valid')
    mockbot.getme.respond(json={
        'ok': True,
        'result': {
            'first_name': 'Valid Bot',
            'id': 1234,
            'username': 'validbot',
        }
    })
    mockbot.getupdates.respond(json={'description': 'Conflict', 'error_code': 409, 'ok': False})

    assert conversation.message('1234:valid') == """\
[chat_id=1000 parse_mode=HTML]
Cool, that API Token is for <code>validbot</code>. Give me another moment...


[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Paste a bot API Token</b>

Woops, it looks like this bot account is already in use. Make sure no other bot programs are running using this API Token and paste the token again, or use another one:
"""

    mockbot.getme.respond(json={
        'ok': True,
        'result': {
            'first_name': 'Valid Bot',
            'id': 1234,
            'username': 'validbot',
        },
    })
    mockbot.getupdates.respond(json={'description': 'Not Found', 'error_code': 404, 'ok': False})

    assert conversation.message('1234:valid') == """\
[chat_id=1000 parse_mode=HTML]
Cool, that API Token is for <code>validbot</code>. Give me another moment...


[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Paste a bot API Token</b>

Woops, while trying to use <code>1234:valid</code> I got error 404 (<code>Not Found</code>).
"""

    mockbot.getme.respond(json={
        'ok': True,
        'result': {
            'first_name': 'Valid Bot',
            'id': 1234,
            'username': 'validbot',
        },
    })
    mockbot.getupdates.respond(json={'ok': True, 'result': []})

    assert conversation.message('1234:valid') == """\
[chat_id=1000 parse_mode=HTML]
Cool, that API Token is for <code>validbot</code>. Give me another moment...


[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Add a bot: <b>Configure your new bot</b>

Yay, I am now running <code>validbot</code> (<code>Valid Bot</code>). Open a private chat with @validbot and type <code>/admin</code> to continue setup.
"""

    assert conversation.multibot.conf['bots'] == {
        'modulestestbot': {
            'issue37': {
                'admin': {
                    'admins': [1000],
                },
                'telegram': {
                    'running': False,
                    'token': '1234:test',
                },
            },
        },
        'validbot': {
            'issue37': {
                'admin': {
                    'admins': [1000],
                },
                'telegram': {
                    'running': True,
                    'token': '1234:valid',
                },
            },
        },
    }


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/newbot \u2013 Set up a new bot
"""
