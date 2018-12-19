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

    assert conversation.message('/admin modulestestbot moderator') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a group</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    adding_user = {'id': 2000}
    joined_user = {'id': 3000, 'is_bot': False}
    chat = {'id': -1001000001000, 'type': 'supergroup', 'title': 'My Group', 'username': 'mygroup'}
    message = {
        'from': adding_user,
        'chat': chat,
        'message_id': 5000,
        'new_chat_members': [joined_user],
    }
    join_update = {'message': message}
    # Let the bot notice it's in the test group.
    conversation.multibot.dispatcher(conversation.bot, join_update)

    assert conversation.message('/admin modulestestbot moderator') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator: <b>Choose a group</b>',
            'reply_markup': {'inline_keyboard': [[{'text': '-1001000001000 (My Group)', 'callback_data': '/admin modulestestbot moderator -1001000001000'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    "I can't set <code>bogus</code>.",
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a greeting: <b>Type a new value for greeting</b>\n'
                    '\n'
                    'How should I greet people when they join?\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('Welcome! <b>Initial</b> pinned message.') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Set <code>greeting</code> to <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    replies = conversation.message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == [
        {
            'chat_id': -1001000001000,
            'disable_notification': True,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome! <b>Initial</b> pinned message.',
        },
    ]  # yapf: disable

    message = {
        'from': adding_user,
        'chat': chat,
        'message_id': 5000,
        'pinned_message': {
            'message_id': 6000,
        },
    }
    pin_update = {'message': message}
    conversation.multibot.dispatcher(conversation.bot, pin_update)

    replies = conversation.message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == [
        {
            'chat_id': -1001000001000,
            'disable_notification': True,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome! <b>Initial</b> <a href="https://t.me/mygroup/6000">pinned message</a>.',
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a greeting: <b>Type a new value for greeting</b>\n'
                    '\n'
                    'How should I greet people when they join?\n'
                    '\n'
                    '<code>greeting</code> is currently <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code>.\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('Welcome! New message.') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Changed <code>greeting</code> from <code>Welcome! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code> to <code>Welcome! New message.</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a greeting: <b>Type a new value for greeting</b>\n'
                    '\n'
                    'How should I greet people when they join?\n'
                    '\n'
                    '<code>greeting</code> is currently <code>Welcome! New message.</code>.\n'
                    '\n'
                    'Type your new value, or type "off" to disable/reset to default.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('OFF') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Unset <code>greeting</code> (was <code>Welcome! New message.</code>).',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting OFF') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Unset <code>greeting</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars \u2022 Which calendars should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'daily \u2022 Should I announce upcoming events once a day? If so, at what hour?', 'callback_data': '/admin modulestestbot moderator -1001000001000 daily'}],
                                                 [{'text': 'dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement.', 'callback_data': '/admin modulestestbot moderator -1001000001000 dailytext'}],
                                                 [{'text': 'greeting \u2022 How should I greet people when they join?', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'maxeventscount \u2022 How many events should be listed in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventscount'}],
                                                 [{'text': 'maxeventsdays \u2022 How many days into the future should /events look?', 'callback_data': '/admin modulestestbot moderator -1001000001000 maxeventsdays'}],
                                                 [{'text': 'timezone \u2022 What time zone should be used in /events?', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable
