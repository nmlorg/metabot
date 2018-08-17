"""Tests for metabot.modules.newbot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import ntelebot
import pytest

from metabot.modules import newbot


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    dispatcher = ntelebot.dispatch.Dispatcher()
    dispatcher.add_command('newbot', newbot)
    return build_conversation(dispatcher)


# pylint: disable=line-too-long


def test_default(conversation, requests_mock):  # pylint: disable=redefined-outer-name
    """Verify the bot doesn't respond to the /admin command from non-admins."""

    assert conversation('/newbot') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
                    '\n'
                    "To create a new bot, let me know your bot account's API Token. This is a code that looks like:\n"
                    '\n'
                    '<pre>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</pre>\n'
                    '\n'
                    'If you are creating a bot entirely from scratch, open a private chat with @BotFather and follow the process at https://core.telegram.org/bots#creating-a-new-bot to create a new bot account. At the end of that process, you will receive an API Token that you can paste here.\n'
                    '\n'
                    'Otherwise, open a private chat with @BotFather, type <code>/mybots</code>, select the bot account you want to use, select <code>API Token</code>, then copy the code and paste it here:',
        },
    ]  # yapf: disable

    requests_mock.post(
        'https://api.telegram.org/botbogus/getme',
        json={
            'description': 'Not Found',
            'error_code': 404,
            'ok': False
        })

    assert conversation('bogus') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
                    '\n'
                    'Woops, while trying to use <code>bogus</code> I got error 404 (<code>Not Found</code>).',
        },
    ]  # yapf: disable

    requests_mock.post(
        'https://api.telegram.org/bot1234:invalid/getme',
        json={
            'description': 'Unauthorized',
            'error_code': 401,
            'ok': False,
        })

    assert conversation('1234:invalid') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
                    '\n'
                    "Woops, Telegram told me <code>1234:invalid</code> is unauthorized, meaning the code is either incomplete or out of date. If you generated it yourself, open a private chat with @BotFather, type <code>/mybots</code>, select the bot account you're trying to use, select <code>API Token</code>, then copy the code and paste it here. If you got the code from someone else, send them these instructions (including the token I used). If the code you got from BotFather isn't working, select <code>Revoke current token</code> to generate a new one, then paste that new one here:",
        },
    ]  # yapf: disable

    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getme',
        json={
            'ok': True,
            'result': {
                'first_name': 'Valid Bot',
                'id': 1234,
                'username': 'validbot'
            }
        })
    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getupdates',
        json={
            'description': 'Conflict',
            'error_code': 409,
            'ok': False,
        })

    assert conversation('1234:valid') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Cool, that API Token is for <code>validbot</code>. Give me another moment...',
        },
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
                    '\n'
                    'Woops, it looks like this bot account is already in use. Make sure no other bot programs are running using this API Token and paste the token again, or use another one:',
        },
    ]  # yapf: disable

    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getme',
        json={
            'ok': True,
            'result': {
                'first_name': 'Valid Bot',
                'id': 1234,
                'username': 'validbot'
            }
        })
    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getupdates',
        json={
            'description': 'Not Found',
            'error_code': 404,
            'ok': False,
        })

    assert conversation('1234:valid') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Cool, that API Token is for <code>validbot</code>. Give me another moment...',
        },
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Paste a bot API Token</b>\n'
                    '\n'
                    'Woops, while trying to use <code>1234:valid</code> I got error 404 (<code>Not Found</code>).',
        },
    ]  # yapf: disable

    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getme',
        json={
            'ok': True,
            'result': {
                'first_name': 'Valid Bot',
                'id': 1234,
                'username': 'validbot'
            }
        })
    requests_mock.post(
        'https://api.telegram.org/bot1234:valid/getupdates', json={
            'ok': True,
            'result': []
        })

    assert conversation('1234:valid') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Cool, that API Token is for <code>validbot</code>. Give me another moment...',
        },
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Add a bot: <b>Configure your new bot</b>\n'
                    '\n'
                    'Yay, I am now running <code>validbot</code> (<code>Valid Bot</code>). Open a private chat with @validbot and type <code>/admin</code> to continue setup.',
        },
    ]  # yapf: disable

    assert conversation.bot.multibot.bots == [
        {
            'modules': {
                'admin': {
                    'admins': [1000],
                },
            },
            'token': '1234:valid',
        },
    ]
