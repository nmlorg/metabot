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
                                                 [{'text': 'help \u2022 Return the list of commands and other bot features', 'callback_data': '/admin modulestestbot help'}],
                                                 [{'text': 'Back', 'callback_data': '/admin'}]]},
        },
    ]  # yapf: disable


def test_bootstrap(conversation):  # pylint: disable=redefined-outer-name
    """Test /_bootstrap."""

    assert conversation.multibot.bots['modulestestbot'].pop('admin') == {'admins': [1000]}
    assert len(admin.BOOTSTRAP_TOKEN) == 32
    admin.BOOTSTRAP_TOKEN = 'bootstraptest'

    assert conversation.message('/_bootstrap') == []
    assert conversation.multibot.bots['modulestestbot'].get('admin') is None

    assert conversation.message('/_bootstrap bogus') == []
    assert conversation.multibot.bots['modulestestbot'].get('admin') is None

    assert conversation.message('/_bootstrap bootstraptest') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Added 1000 to the admin list.',
        },
    ]  # yapf: disable
    assert conversation.multibot.bots['modulestestbot'].get('admin') == {'admins': [1000]}

    assert conversation.message('/_bootstrap bootstraptest') == []
    assert conversation.multibot.bots['modulestestbot'].get('admin') == {'admins': [1000]}

    assert conversation.message('/_bootstrap bootstraptest', user_id=2000) == []
    assert conversation.multibot.bots['modulestestbot'].get('admin') == {'admins': [1000]}


def test_admins(conversation):  # pylint: disable=redefined-outer-name
    """Verify /admin's own configurator."""

    assert conversation.message('/admin modulestestbot admin') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
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
                    "I'm not sure what <code>bogus value</code> is\u2014it's not a user id!\n"
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
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
                    "You can't remove yourself from the admin list.\n"
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
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
                    'Added 2000 to the admin list.\n'
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin bogus value') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    "I'm not sure what <code>bogus value</code> is\u2014it's not a user id!\n"
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove 2000', 'callback_data': '/admin modulestestbot admin 2000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot admin 2000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a admin: <b>Choose an admin</b>\n'
                    '\n'
                    'Removed 2000 from the admin list.\n'
                    '\n'
                    'Forward a message from a user to add or remove them, or select an existing admin to remove.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable
