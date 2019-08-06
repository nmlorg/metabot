"""Tests for metabot.modules.events."""

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
Bot Admin › modulestestbot › moderator › -1001000001000 › calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars should be listed in /events?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /admin modulestestbot moderator -1001000001000 calendars remove 6fc2c510]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    conversation.bot.config['issue37']['moderator']['-1001000001000']['timezone'] = 'US/Pacific'

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVUy9QYWNpZmlj">NOW, Wed 31ˢᵗ, 4:16–4:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
"""

    conversation.bot.config['issue37']['moderator']['-1001000001000']['timezone'] = 'UTC'

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">NOW, Thu 1ˢᵗ, 12:16–12:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">1 week on Thu 8ᵗʰ, 12–1 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""

    conversation.bot.config['issue37']['moderator']['-1001000001000']['maxeventscount'] = 1

    assert conversation.message('/events', chat_type='supergroup') == """\
[chat_id=-1001000001000 disable_web_page_preview=True parse_mode=HTML reply_to_message_id=2000]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">NOW, Thu 1ˢᵗ, 12:16–12:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
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
Events › Settings: <b>Choose a field</b>
[calendars • Which calendars do you want to see? | /events set calendars]
[timezone • What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.message('/events set calendars') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    conversation.bot.config['issue37']['events']['users']['1000']['timezone'] = 'US/Pacific'

    assert conversation.message('/events') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVUy9QYWNpZmlj">NOW, Wed 31ˢᵗ, 4:16–4:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

Alpha Description
[\xa0 | /stop] [Settings | /events set] [Next | /events 6fc2c510:bravo]
"""

    assert conversation.message('/events 6fc2c510:bravo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVUy9QYWNpZmlj">1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

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
Events › Settings › calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    conversation.bot.config['issue37']['events']['users']['1000']['timezone'] = 'US/Pacific'

    assert conversation.raw_inline('events') == [
        {
            'cache_time': 30,
            'inline_query_id': 2000,
            'is_personal': True,
            'switch_pm_text': 'Settings',
            'switch_pm_parameter': 'L2V2ZW50cyBzZXQ',
            'results': [
                {
                    'description': 'NOW, Wed 31ˢᵗ, 4:16–4:33 pm @ Alpha Venue',
                    'id': '6fc2c510:alpha',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Alpha Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVUy9QYWNpZmlj">NOW, Wed 31ˢᵗ, 4:16–4:33 pm</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Alpha Summary',
                    'type': 'article',
                },
                {
                    'description': '1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVUy9QYWNpZmlj">1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary',
                    'type': 'article',
                },
                {
                    'description': '1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm @ Charlie Venue',
                    'id': '6fc2c510:charlie',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Charlie Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVTL1BhY2lmaWM">1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>',
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
                    'description': '1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm @ Bravo Venue',
                    'id': '6fc2c510:bravo',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<b>Bravo Summary</b>\n'
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVUy9QYWNpZmlj">1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>',
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
                                        '<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVUy9QYWNpZmlj">1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>\n'
                                        '\n'
                                        'Bravo Description',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Bravo Summary • 1 week on Wed, Jan (1970) 7ᵗʰ, 4–5 pm @ Bravo Venue',
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
Events › Settings: <b>Choose a field</b>
[calendars • Which calendars do you want to see? | /events set calendars]
[timezone • What time zone are you in? | /events set timezone]
[Back | /events]
"""

    assert conversation.message('/events set calendars') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

Added <code>6fc2c510</code> to your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

<code>6fc2c510</code> is already in your calendar view!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Remove Test Calendar | /events set calendars remove 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars remove 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

Removed <code>6fc2c510</code> from your calendar view.

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars remove 6fc2c510') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

<code>6fc2c510</code> is not in your calendar view!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set calendars add bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings › calendars: <b>Select a calendar</b>

<code>bogus</code> is not a calendar!

Which calendars do you want to see?

Select a calendar to add or remove from the list below:
[Add Test Calendar | /events set calendars add 6fc2c510]
[Back | /events set]
"""

    assert conversation.message('/events set bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Events › Settings: <b>Choose a field</b>

I can't set <code>bogus</code>.
[calendars • Which calendars do you want to see? | /events set calendars]
[timezone • What time zone are you in? | /events set timezone]
[Back | /events]
"""


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/events – Display recent and upcoming events
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
        "Visit @MYGROUP • Also, there's an event coming up:\n"
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
    # yapf: enable


def test_daily_messages(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test daily announcement logic."""

    monkeypatch.setattr('time.time', lambda: 0)

    replies = conversation.raw_message('/dummy')
    assert conversation.format_messages(replies) == ''

    records = {}
    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {}
    assert conversation.format_messages(replies) == ''

    conversation.bot.config['issue37']['moderator']['-1002000002000'] = {
        'calendars': '6fc2c510',
        'daily': {
            'hour': 0,
        },
        'timezone': 'UTC',
    }

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Alpha Description',
            'end': 2000,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Alpha Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == """\
[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">TODAY, Thu 1ˢᵗ, 12:16–12:33 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">1 week on Thu 8ᵗʰ, 12–1 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""
    replies.clear()

    conversation.bot.config['issue37']['moderator']['-1002000002000']['daily']['hour'] = 1

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Alpha Description',
            'end': 2000,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Alpha Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == ''

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['summary'] = 'Edited Summary'
    cal.events['6fc2c510:alpha']['end'] += 60

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Alpha Description',
            'end': 2060,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Edited Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == """\
[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">TODAY, Thu 1ˢᵗ, 12:16–12:34 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
• <i>Alpha Summary</i> → <b>Edited Summary</b>
• <i>…12:33 am</i> → <b>…12:34 am</b>


[chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">TODAY, Thu 1ˢᵗ, 12:16–12:34 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">1 week on Thu 8ᵗʰ, 12–1 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated</a>]
"""
    replies.clear()

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Alpha Description',
            'end': 2060,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Edited Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == ''

    monkeypatch.setattr('time.time', lambda: 1000)

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Alpha Description',
            'end': 2060,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Edited Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == ''

    cal.events['6fc2c510:alpha']['description'] = 'Multi\nLine\nDescription'
    cal.events['6fc2c510:new'] = {
        'description': 'New Description',
        'end': 3000,
        'local_id': '6fc2c510:new',
        'location': 'New Venue, Rest of New Location',
        'start': 2000,
        'summary': 'New Summary',
    }
    conversation.multibot.multical.ordered.append(cal.events['6fc2c510:new'])
    conversation.multibot.multical._rebuild()  # pylint: disable=protected-access

    events._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
    assert records == {
        ('modulestestbot', '-1002000002000'): (0, [{
            'description': 'Multi\nLine\nDescription',
            'end': 2060,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 1000,
            'summary': 'Edited Summary',
        }, {
            'description': 'New Description',
            'end': 3000,
            'local_id': '6fc2c510:new',
            'location': 'New Venue, Rest of New Location',
            'start': 2000,
            'summary': 'New Summary',
        }, {
            'description': 'Bravo Description',
            'end': 608400,
            'local_id': '6fc2c510:bravo',
            'location': 'Bravo Venue, Rest of Bravo Location',
            'start': 604800,
            'summary': 'Bravo Summary',
        }], {
            'message_id': 12345,
        }),
    }
    assert conversation.format_messages(replies) == """\
[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Added:

<b>New Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">TODAY, Thu 1ˢᵗ, 12:33–12:50 am</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>

Updated:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">NOW, Thu 1ˢᵗ, 12:16–12:34 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
• <i>Alpha Description</i> → <b>Multi Line Description</b>


[chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a few events coming up:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">NOW, Thu 1ˢᵗ, 12:16–12:34 am</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>New Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">TODAY, Thu 1ˢᵗ, 12:33–12:50 am</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">1 week on Thu 8ᵗʰ, 12–1 am</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated</a>]
"""


def test_quick_diff():
    """Test description string differ."""

    # pylint: disable=protected-access
    assert events._quick_diff('', '') == ('', '')
    assert events._quick_diff('AAAAB', 'AAAABnew') == ('AAAAB', 'AAAABnew')
    assert events._quick_diff('AAAABC', 'AAAABCnew') == ('…AABC', '…AABCnew')
    assert events._quick_diff('AAAABCold', 'AAAABC') == ('…AABCold', '…AABC')
    assert events._quick_diff('AAAABCold', 'AAAABCnew') == ('…AABCold', '…AABCnew')
    assert events._quick_diff(
        'AAAAB', 'AAAAB6789012345678901234567890') == ('AAAAB', 'AAAAB6789012345678901234567890')
    assert events._quick_diff(
        'AAAAB', 'AAAAB6789012345678901234567890Z') == ('AAAAB', 'AAAAB678901234567890123456789…')
    assert events._quick_diff(
        'AAAABC', 'AAAABC6789012345678901234567890') == ('…AABC', '…AABC6789012345678901234567890')
    assert events._quick_diff(
        'AAAABC', 'AAAABC6789012345678901234567890Z') == ('…AABC', '…AABC678901234567890123456789…')
