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
            'text': "I'm not configured for this group! Ask a bot admin to go into the <b>moderator</b> module settings, group <b>-1001000001000</b>, and choose one or more calendars and set the time zone.",
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

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>\n'
                    '\n'
                    'Choose a time zone:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Africa', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Africa'}],
                                                 [{'text': 'America', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America'}],
                                                 [{'text': 'Antarctica', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Antarctica'}],
                                                 [{'text': 'Arctic', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Arctic'}],
                                                 [{'text': 'Asia', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Asia'}],
                                                 [{'text': 'Atlantic', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Atlantic'}],
                                                 [{'text': 'Australia', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Australia'}],
                                                 [{'text': 'Canada', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Canada'}],
                                                 [{'text': 'Europe', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Europe'}],
                                                 [{'text': 'GMT', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone GMT'}],
                                                 [{'text': 'Indian', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Indian'}],
                                                 [{'text': 'Pacific', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone Pacific'}],
                                                 [{'text': 'US', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US'}],
                                                 [{'text': 'UTC', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone UTC'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone US') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>\n'
                    '\n'
                    'Choose a time zone:',
            'reply_markup': {'inline_keyboard': [[{'text': 'US/Alaska', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Alaska'}],
                                                 [{'text': 'US/Arizona', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Arizona'}],
                                                 [{'text': 'US/Central', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Central'}],
                                                 [{'text': 'US/Eastern', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Eastern'}],
                                                 [{'text': 'US/Hawaii', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Hawaii'}],
                                                 [{'text': 'US/Mountain', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Mountain'}],
                                                 [{'text': 'US/Pacific', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone US/Pacific'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone America/Indiana') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>\n'
                    '\n'
                    'Choose a time zone:',
            'reply_markup': {'inline_keyboard': [[{'text': 'America/Indiana/Indianapolis', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Indianapolis'}],
                                                 [{'text': 'America/Indiana/Knox', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Knox'}],
                                                 [{'text': 'America/Indiana/Marengo', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Marengo'}],
                                                 [{'text': 'America/Indiana/Petersburg', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Petersburg'}],
                                                 [{'text': 'America/Indiana/Tell_City', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Tell_City'}],
                                                 [{'text': 'America/Indiana/Vevay', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vevay'}],
                                                 [{'text': 'America/Indiana/Vincennes', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vincennes'}],
                                                 [{'text': 'America/Indiana/Winamac', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone America/Indiana/Winamac'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator -1001000001000'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone US/Pacific') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Set timezone to <code>US/Pacific</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'timezone', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events', chat_type='supergroup') == [
        {
            'chat_id': -1001000001000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 2000,
            'text': '<b>Alpha Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>\n'
                    '\n'
                    '<b>Bravo Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone UTC') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>\n'
                    '\n'
                    'Set timezone to <code>UTC</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/admin modulestestbot moderator -1001000001000 calendars'}],
                                                 [{'text': 'greeting', 'callback_data': '/admin modulestestbot moderator -1001000001000 greeting'}],
                                                 [{'text': 'timezone', 'callback_data': '/admin modulestestbot moderator -1001000001000 timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot moderator'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events', chat_type='supergroup') == [
        {
            'chat_id': -1001000001000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 2000,
            'text': '<b>Alpha Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Thu 1, 12:16\u201312:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>\n'
                    '\n'
                    '<b>Bravo Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Wed 7, 12:33\u20131:33 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
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
            'text': 'Events \u203a Settings: <b>Choose a field</b>\n'
                    '\n'
                    'Please choose one or more calendars and set your time zone!',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/events set calendars'}],
                                                 [{'text': 'timezone', 'callback_data': '/events set timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set calendars add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set calendars remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set timezone US/Pacific') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Choose a field</b>\n'
                    '\n'
                    'Set timezone to <code>US/Pacific</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/events set calendars'}],
                                                 [{'text': 'timezone', 'callback_data': '/events set timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Alpha Summary</b>\n'
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>\n'
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
                    '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
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
            'switch_pm_text': 'Click to choose one or more calendars and set your time zone!',
            'switch_pm_parameter': 'L2V2ZW50cw',
            'results': [],
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set calendars remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set timezone US/Pacific') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Choose a field</b>\n'
                    '\n'
                    'Set timezone to <code>US/Pacific</code>.',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/events set calendars'}],
                                                 [{'text': 'timezone', 'callback_data': '/events set timezone'}],
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
                    'description': 'TODAY, Wed 31, 4:16\u20134:33 pm @ Alpha Venue',
                    'id': '6fc2c510:alpha',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Alpha Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Alpha Summary',
                    'type': 'article',
                },
                {
                    'description': 'this Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
                {
                    'description': 'this Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Charlie Venue',
                    'id': '6fc2c510:charlie',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Charlie Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGll">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>',
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
                    'description': 'this Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
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
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">this Tue, Jan (1970) 6, 4:33\u20135:33 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
                                        '\n'
                                        'Bravo Description',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary \u2022 this Tue, Jan (1970) 6, 4:33\u20135:33 pm @ Bravo Venue',
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
            'text': 'Events \u203a Settings: <b>Choose a field</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/events set calendars'}],
                                                 [{'text': 'timezone', 'callback_data': '/events set timezone'}],
                                                 [{'text': 'Back', 'callback_data': '/events'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set calendars add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Added <code>6fc2c510</code> to your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set calendars remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>6fc2c510</code> is already in your calendar view!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Remove Test Calendar', 'callback_data': '/events set calendars remove 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars remove 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    'Removed <code>6fc2c510</code> from your calendar view.\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set calendars add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars remove 6fc2c510') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>6fc2c510</code> is not in your calendar view!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set calendars add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings \u203a calendars: <b>Select a calendar</b>\n'
                    '\n'
                    '<code>bogus</code> is not a calendar!\n'
                    '\n'
                    'Select a calendar to add or remove from the list below:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Add Test Calendar', 'callback_data': '/events set calendars add 6fc2c510'}],
                                                 [{'text': 'Back', 'callback_data': '/events set'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/events set bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Events \u203a Settings: <b>Choose a field</b>\n'
                    '\n'
                    "I can't set <code>bogus</code>.",
            'reply_markup': {'inline_keyboard': [[{'text': 'calendars', 'callback_data': '/events set calendars'}],
                                                 [{'text': 'timezone', 'callback_data': '/events set timezone'}],
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
