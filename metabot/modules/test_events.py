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
            'end': 60 * 60 * 24 * 7 + 60 * 60,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 60 * 60 * 24 * 7,
            'summary': 'Bravo Summary',
        },
        '6fc2c510:charlie': {
            'description': 'Charlie Description',
            'end': 60 * 60 * 24 * 7 + 1 + 60 * 60,
            'local_id': '6fc2c510:charlie',
            'location': 'Charlie Venue, Rest of Charlie Location',
            'start': 60 * 60 * 24 * 7 + 1,
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

    assert conversation.message('/notevents') == ''

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
I'm not configured for this group! Ask a bot admin to go into the <b>moderator</b> module settings, group <b>-1001000001000</b>, and choose one or more calendars and set the time zone.
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars should be listed in /events?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /admin modulestestbot moderator -1001000001000 calendars remove 6fc2c510]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[Africa | /admin modulestestbot moderator -1001000001000 timezone Africa]
[America | /admin modulestestbot moderator -1001000001000 timezone America]
[Antarctica | /admin modulestestbot moderator -1001000001000 timezone Antarctica]
[Arctic | /admin modulestestbot moderator -1001000001000 timezone Arctic]
[Asia | /admin modulestestbot moderator -1001000001000 timezone Asia]
[Atlantic | /admin modulestestbot moderator -1001000001000 timezone Atlantic]
[Australia | /admin modulestestbot moderator -1001000001000 timezone Australia]
[\xa0 | /stop] [Next | /admin modulestestbot moderator -1001000001000 timezone - 1]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone - 1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[Canada | /admin modulestestbot moderator -1001000001000 timezone Canada]
[Europe | /admin modulestestbot moderator -1001000001000 timezone Europe]
[GMT | /admin modulestestbot moderator -1001000001000 timezone GMT]
[Indian | /admin modulestestbot moderator -1001000001000 timezone Indian]
[Pacific | /admin modulestestbot moderator -1001000001000 timezone Pacific]
[US | /admin modulestestbot moderator -1001000001000 timezone US]
[UTC | /admin modulestestbot moderator -1001000001000 timezone UTC]
[Prev | /admin modulestestbot moderator -1001000001000 timezone - 0] [\xa0 | /stop]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone',
                                language_code='en-us') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[US/Alaska | /admin modulestestbot moderator -1001000001000 timezone US/Alaska]
[US/Arizona | /admin modulestestbot moderator -1001000001000 timezone US/Arizona]
[US/Central | /admin modulestestbot moderator -1001000001000 timezone US/Central]
[US/Eastern | /admin modulestestbot moderator -1001000001000 timezone US/Eastern]
[US/Hawaii | /admin modulestestbot moderator -1001000001000 timezone US/Hawaii]
[US/Mountain | /admin modulestestbot moderator -1001000001000 timezone US/Mountain]
[US/Pacific | /admin modulestestbot moderator -1001000001000 timezone US/Pacific]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone',
                                language_code='en-ca') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[Canada/Atlantic | /admin modulestestbot moderator -1001000001000 timezone Canada/Atlantic]
[Canada/Central | /admin modulestestbot moderator -1001000001000 timezone Canada/Central]
[Canada/Eastern | /admin modulestestbot moderator -1001000001000 timezone Canada/Eastern]
[Canada/Mountain | /admin modulestestbot moderator -1001000001000 timezone Canada/Mountain]
[Canada/Newfoundland | /admin modulestestbot moderator -1001000001000 timezone Canada/Newfoundland]
[Canada/Pacific | /admin modulestestbot moderator -1001000001000 timezone Canada/Pacific]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone',
                                language_code='en-gb') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[Europe/London | /admin modulestestbot moderator -1001000001000 timezone Europe/London]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone America/Indiana') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[America/Indiana/Indianapolis | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Indianapolis]
[America/Indiana/Knox | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Knox]
[America/Indiana/Marengo | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Marengo]
[America/Indiana/Petersburg | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Petersburg]
[America/Indiana/Tell_City | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Tell_City]
[America/Indiana/Vevay | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vevay]
[America/Indiana/Vincennes | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vincennes]
[\xa0 | /stop] [Next | /admin modulestestbot moderator -1001000001000 timezone America/Indiana 1]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone America/Indiana 1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000 \u203a timezone: <b>Choose a time zone</b>

What time zone should be used in /events?

Choose a time zone:
[America/Indiana/Winamac | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Winamac]
[Prev | /admin modulestestbot moderator -1001000001000 timezone America/Indiana 0] [\xa0 | /stop]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone US/Pacific') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>

Set timezone to <code>US/Pacific</code>.
[calendars \u2022 Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily \u2022 Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[greeting \u2022 How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount \u2022 How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays \u2022 How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone \u2022 What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone UTC') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>

Set timezone to <code>UTC</code>.
[calendars \u2022 Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily \u2022 Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[greeting \u2022 How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount \u2022 How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays \u2022 How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone \u2022 What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Thu 1, 12:16\u201312:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">1 week on Thu 8, 12\u20131 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 maxeventscount 1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a moderator \u203a -1001000001000: <b>Choose a field</b>

Set <code>maxeventscount</code> to <code>1</code>.
[calendars \u2022 Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily \u2022 Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailytext \u2022 One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[greeting \u2022 How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount \u2022 How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays \u2022 How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone \u2022 What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Thu 1, 12:16\u201312:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
"""

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
No events in the next 6 days!
"""


def test_private(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test /events in a private chat."""

    assert conversation.message('/events') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Please choose one or more calendars and set your time zone!
[Settings | /events set]
"""

    assert conversation.message('/events set') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings: <b>Choose a field</b>
[calendars \u2022 Which calendars do you want to see? | /events set calendars]
[timezone \u2022 What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.message('/events set calendars') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set timezone US/Pacific') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings: <b>Choose a field</b>

Set timezone to <code>US/Pacific</code>.
[calendars \u2022 Which calendars do you want to see? | /events set calendars]
[timezone \u2022 What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.message('/events') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYQ">TODAY, Wed 31, 4:16\u20134:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

Alpha Description
[\xa0 | /stop] [Settings | /events set] [Next | /events 6fc2c510:bravo]
"""

    assert conversation.message('/events 6fc2c510:bravo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">1 week on Wed, Jan (1970) 7, 4\u20135 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

Bravo Description
[Prev | /events 6fc2c510:alpha] [Current | /events] [Next | /events 6fc2c510:charlie]
"""

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.message('/events') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
No upcoming events!
[\xa0 | /stop] [Settings | /events set] [\xa0 | /stop]
"""


def test_inline(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test @BOTUSER events."""

    assert conversation.raw_inline('events') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Click to choose one or more calendars and set your time zone!',
            'switch_pm_parameter': 'L2V2ZW50cw',
            'results': [],
        },
    ]  # yapf: disable

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set timezone US/Pacific') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings: <b>Choose a field</b>

Set timezone to <code>US/Pacific</code>.
[calendars \u2022 Which calendars do you want to see? | /events set calendars]
[timezone \u2022 What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.raw_inline('events') == [
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
                    'description': '1 week on Wed, Jan (1970) 7, 4\u20135 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">1 week on Wed, Jan (1970) 7, 4\u20135 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
                {
                    'description': '1 week on Wed, Jan (1970) 7, 4\u20135 pm @ Charlie Venue',
                    'id': '6fc2c510:charlie',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Charlie Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGll">1 week on Wed, Jan (1970) 7, 4\u20135 pm</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Charlie Summary',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    assert conversation.raw_inline('events bra') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [
                {
                    'description': '1 week on Wed, Jan (1970) 7, 4\u20135 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">1 week on Wed, Jan (1970) 7, 4\u20135 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    assert conversation.raw_inline('events full bra') == [
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
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2bw">1 week on Wed, Jan (1970) 7, 4\u20135 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
                                        '\n'
                                        'Bravo Description',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary \u2022 1 week on Wed, Jan (1970) 7, 4\u20135 pm @ Bravo Venue',
                    'type': 'article',
                },
            ],
        },
    ]  # yapf: disable

    monkeypatch.setattr('time.time', lambda: 2000000.)

    assert conversation.raw_inline('events') == [
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

    assert conversation.message('/events set') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings: <b>Choose a field</b>
[calendars \u2022 Which calendars do you want to see? | /events set calendars]
[timezone \u2022 What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.message('/events set calendars') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

<code>6fc2c510</code> is already in your calendar view!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars remove 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

Removed <code>6fc2c510</code> from your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars remove 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

<code>6fc2c510</code> is not in your calendar view!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings \u203a calendars: <b>Select a calendar</b>

<code>bogus</code> is not a calendar!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events \u203a Settings: <b>Choose a field</b>

I can't set <code>bogus</code>.
[calendars \u2022 Which calendars do you want to see? | /events set calendars]
[timezone \u2022 What time zone are you in? | /events set timezone]
[Back | /events]
"""


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/events \u2013 Display recent and upcoming events
"""


def test_format_daily_message():  # pylint: disable=missing-docstring
    # yapf: disable - pylint: disable=protected-access
    assert events._format_daily_message('', ['EVENT1']) == (
        "There's an event coming up:\n"
        '\n'
        'EVENT1')
    assert events._format_daily_message('', ['EVENT1', 'EVENT2']) == (
        "There are a couple events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2')
    assert events._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3']) == (
        "There are a few events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3')
    assert events._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4']) == (
        "There are a bunch of events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3\n'
        'EVENT4')
    assert events._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4', 'EVENT5']) == (
        "There are a bunch of events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3\n'
        'EVENT4\n'
        'EVENT5')

    assert events._format_daily_message('1 + 1 = 2!', ['EVENT1']) == (
        "1 + 1 = 2! Also, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert events._format_daily_message('Visit @MYGROUP', ['EVENT1']) == (
        "Visit @MYGROUP \u2022 Also, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert events._format_daily_message('I love events.', ['EVENT1']) == (
        "I love events. Speaking of which, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert events._format_daily_message('I love events:', ['EVENT1']) == (
        "I love events:\n"
        '\n'
        'EVENT1')
