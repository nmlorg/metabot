"""Tests for metabot.modules.moderator."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(moderator)


# pylint: disable=line-too-long


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME moderator."""

    assert conversation('/admin modulestestbot moderator') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a group</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    adding_user = {'id': 2000}
    joined_user = {'id': 3000}
    chat = {'id': -4000, 'type': 'supergroup', 'title': 'My Group'}
    message = {
        'from': adding_user,
        'chat': chat,
        'message_id': 5000,
        'new_chat_members': [joined_user],
    }
    update = {'message': message}
    conversation.multibot.dispatcher(conversation.bot, update)

    assert conversation('/admin modulestestbot moderator') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a group</b>',
            'reply_markup': {'inline_keyboard': [[{'text': '-4000 (My Group)', 'callback_data': '/admin modulestestbot moderator -4000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000 bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>\n'
                    '\n'
                    "I can't set <code>bogus</code>.",
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Type a new value for greeting</b>\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -4000'}]]},
        },
    ]  # yapf: disable

    assert conversation('Welcome! <b>Initial</b> message.') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>\n'
                    '\n'
                    'Set <code>greeting</code> to <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; message.</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    replies = conversation('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, update)
    assert replies == [
        {
            'chat_id': -4000,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome! <b>Initial</b> message.',
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Type a new value for greeting</b>\n'
                    '\n'
                    '<code>greeting</code> is currently <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; message.</code>.\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -4000'}]]},
        },
    ]  # yapf: disable

    assert conversation('Welcome! New message.') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>\n'
                    '\n'
                    'Changed <code>greeting</code> from <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; message.</code> to <code>Welcome! New message.</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Type a new value for greeting</b>\n'
                    '\n'
                    '<code>greeting</code> is currently <code>Welcome! New message.</code>.\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -4000'}]]},
        },
    ]  # yapf: disable

    assert conversation('OFF') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>\n'
                    '\n'
                    'Unset <code>greeting</code> (was <code>Welcome! New message.</code>).',
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot moderator -4000 greeting OFF') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a field</b>\n'
                    '\n'
                    'Unset <code>greeting</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -4000 greeting'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable