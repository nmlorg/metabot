"""Tests for metabot.modules.admin."""

from __future__ import absolute_import, division, print_function, unicode_literals

import ntelebot
import pytest

from metabot.modules import admin


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    dispatcher = ntelebot.dispatch.Dispatcher()
    dispatcher.add_command('admin', admin)
    conv = build_conversation(dispatcher)
    conv.bot.config['modules']['admin'] = {'admins': [1000]}
    return conv


# pylint: disable=line-too-long


def test_invalid_user(conversation):  # pylint: disable=redefined-outer-name
    """Verify the bot doesn't respond to the /admin command from non-admins."""

    error_message = [
        {
            'chat_id': 2000,
            'parse_mode': 'HTML',
            'text': "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by opening a chat with me (@modulestestbot) and typing:\n"
                    '\n'
                    '<pre>/admin admins add 2000</pre>',
        },
    ]  # yapf: disable

    assert conversation('/admin', user_id=2000) == error_message
    assert conversation('/admin admins', user_id=2000) == error_message
    assert conversation('/admin admins add 2000', user_id=2000) == error_message
    assert conversation('/admin bogus', user_id=2000) == error_message


def test_default(conversation):  # pylint: disable=redefined-outer-name
    """Verify the /admin command gives its lovely menu of subcommands."""

    assert conversation('/admin') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin: <b>Select a command</b>\n',
            'reply_markup': {'inline_keyboard': [[{'text': 'Admin List', 'callback_data': '/admin admins'}]]},
        },
    ]  # yapf: disable


def test_admins(conversation):  # pylint: disable=redefined-outer-name
    """Verify the /admin admins subcommand."""

    assert conversation('/admin admins') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('bogus value') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "I'm not sure what <code>bogus value</code> is--it's not a user id!",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('1000') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    '1000 is already an admin.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('2000') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    'Added 2000 to the admin list.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin admins remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin admins remove bogus value') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "I'm not sure what <code>bogus value</code> is--it's not an admin!",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin admins remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin admins remove 3000') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "Oops, looks like 3000 isn't an admin [any more?].",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin admins remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin admins remove 1000') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    "You can't remove yourself from the admin list.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin admins remove 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin admins remove 2000') == [
        {
            'chat_id': 1000,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a Admin List: <b>Choose an admin</b>\n'
                    '\n'
                    'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, or select an existing admin to remove.\n'
                    '\n'
                    'Removed 2000 from the admin list.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable
