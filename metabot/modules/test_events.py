"""Tests for metabot.modules.events."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.calendars import loader
from metabot.modules import events
from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation, monkeypatch):  # pylint: disable=missing-docstring
    monkeypatch.setattr('time.time', lambda: 2000.)

    cal = loader.get('static:test_events')
    assert cal.calcode == '6fc2c510'
    cal.events = {
        '6fc2c510:alpha': {
            'description': 'Alpha Description',
            'end': 2000,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Alpha Summary',
        },
        '6fc2c510:bravo': {
            'description': 'Bravo Description',
            'end': 2000 + 60 * 60 * 24 * 6 + 60 * 60,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 2000 + 60 * 60 * 24 * 6,
            'summary': 'Bravo Summary',
        },
        '6fc2c510:charlie': {
            'description': 'Charlie Description',
            'end': 2000 + 60 * 60 * 24 * 6 + 1 + 60 * 60,
            'local_id': '6fc2c510:charlie',
            'location': 'Charlie Venue, Rest of Charlie Location',
            'start': 2000 + 60 * 60 * 24 * 6 + 1,
            'summary': 'Charlie Summary',
        },
    }

    conv = build_conversation(events, moderator)
    conv.multibot.multical.add('static:test_events')
    conv.multibot.calendars['6fc2c510'] = {'name': 'Test Calendar'}
    return conv


# pylint: disable=line-too-long


def test_group(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test /events in a group chat."""

    assert conversation.message('/notevents') == []
    assert conversation.message('/events', chat_type='supergroup') == [
        {
            'chat_id': -1001000001000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 2000,
            'text': "I'm not configured for this group! Ask a bot admin to go into the <code>moderator</code> module settings, group <code>-1001000001000</code>, and set <code>calendars</code> to this group's calendars.",
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 calendars add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events', chat_type='supergroup') == [
        {
            'chat_id': -1001000001000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 2000,
            'text': '<b>Alpha Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>\n'
                    '\n'
                    '<b>Bravo Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
        },
    ]  # yapf: disable

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.message('/events', chat_type='supergroup') == [
        {
            'chat_id': -1001000001000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 2000,
            'text': 'No upcoming events!',
        },
    ]  # yapf: disable


def test_private(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test /events in a private chat."""

    assert conversation.message('/events') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Alpha Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>\n'
                    '\n'
                    'Alpha Description',
            'reply_markup': {'inline_keyboard': [[{'text': '', 'callback_data': '/stop'},
                                                  {'text': 'Settings', 'callback_data': '/events set'},
                                                  {'text': 'Next', 'callback_data': '/events 6fc2c510:bravo'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events 6fc2c510:bravo') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Bravo Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
                    '\n'
                    'Bravo Description',
            'reply_markup': {'inline_keyboard': [[{'text': 'Prev', 'callback_data': '/events 6fc2c510:alpha'},
                                                  {'text': 'Current', 'callback_data': '/events'},
                                                  {'text': 'Next', 'callback_data': '/events 6fc2c510:charlie'}]]},
        },
    ]  # yapf: disable

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.message('/events') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'No upcoming events!',
            'reply_markup': {'inline_keyboard': [[{'text': '', 'callback_data': '/stop'},
                                                  {'text': 'Settings', 'callback_data': '/events set'},
                                                  {'text': '', 'callback_data': '/stop'}]]},
        },
    ]  # yapf: disable


def test_inline(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test @BOTUSER events."""

    assert conversation.inline('events') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Setup',
            'switch_pm_parameter': 'L2V2ZW50cw',
            'results': [],
        },
    ]  # yapf: disable

    assert conversation.message('/events set add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.inline('events') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [
                {
                    'description': 'Wed 31, 4:16\u20134:33 pm @ Alpha Venue',
                    'id': '6fc2c510:alpha',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Alpha Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Alpha Summary',
                    'type': 'article',
                },
                {
                    'description': 'Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
                {
                    'description': 'Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Charlie Venue',
                    'id': '6fc2c510:charlie',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Charlie Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGll">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Charlie Summary',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    assert conversation.inline('events bra') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [
                {
                    'description': 'Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    assert conversation.inline('events full bra') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [
                {
                    'description': 'Bravo Description',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
                                        '\n'
                                        'Bravo Description',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary \u2022 Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.inline('events') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [],
        },
    ]  # yapf: disable


def test_settings(conversation):  # pylint: disable=redefined-outer-name
    """Test /events set."""

    assert conversation.message('/events set') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>6fc2c510</code> is already in your calendar view!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set remove 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    'Removed <code>6fc2c510</code> from your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set remove 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>6fc2c510</code> is not in your calendar view!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set add bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>bogus</code> is not a calendar!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    assert conversation.message('/help', user_id=2000) == [
        {
            'chat_id': 2000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Commands</b>\n'
                    '\n'
                    '/events \u2013 Display recent and upcoming events',
        },
    ]  # yapf: disable
