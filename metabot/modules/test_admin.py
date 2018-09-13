"""Tests for metabot.modules.admin."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import admin


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(admin)


# pylint: disable=line-too-long


def test_invalid_user(conversation):  # pylint: disable=redefined-outer-name
    """Verify the bot doesn't respond to the /admin command from non-admins."""

    error_message = [
        {
            'chat_id': 2000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by opening a chat with me (@modulestestbot) and typing:\n"
                    '\n'
                    '<pre>/admin modulestestbot admin add 2000</pre>',
            'reply_markup': {'inline_keyboard': []},
        },
    ]  # yapf: disable

    assert conversation.message('/admin', user_id=2000) == error_message
    assert conversation.message('/admin dummy', user_id=2000) == error_message
    assert conversation.message(
        '/admin modulestestbot admin add 2000', user_id=2000) == error_message


def test_default(conversation):  # pylint: disable=redefined-outer-name
    """Verify the /admin command gives its lovely menu of subcommands."""

    assert conversation.message('/notadmin') == []
    assert conversation.message('/admin') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin: <b>Choose a bot</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'modulestestbot', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot: <b>Choose a module</b>',
            'reply_markup': {'inline_keyboard': [[{'text': "admin \u2022 Manage the bot's state and settings", 'callback_data': '/admin modulestestbot admin'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable


def test_admins(conversation):  # pylint: disable=redefined-outer-name
    """Verify /admin's own configurator."""

    assert conversation.message('/admin modulestestbot admin') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('bogus value') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "I'm not sure what <code>bogus value</code> is\u2014it's not a user id!",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('1000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    '1000 is already an admin.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('2000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    'Added 2000 to the admin list.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin remove bogus value') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "I'm not sure what <code>bogus value</code> is\u2014it's not an admin!",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin remove 3000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "Oops, looks like 3000 isn't an admin [any more?].",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin remove 1000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "You can't remove yourself from the admin list.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin remove 2000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    'Removed 2000 from the admin list.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable
