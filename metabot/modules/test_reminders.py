"""Tests for metabot.modules.reminders."""

import datetime

import pytest
import pytz
import yaml

from metabot.calendars import loader
from metabot.modules import events
from metabot.modules import moderator
from metabot.modules import reminders

# pylint: disable=too-many-lines


@pytest.fixture
def conversation(build_conversation, monkeypatch):  # pylint: disable=missing-docstring
    monkeypatch.setattr('time.time', lambda: 2000.)

    cal = loader.get('static:test_events')
    assert cal.calcode == '6fc2c510'
    cal.events = {
        '6fc2c510:alpha': {
            'description': 'Alpha Description',
            'end': 60 * 60 * 3.5,
            'local_id': '6fc2c510:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 60 * 60 * 2.5,
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
            'end': 60 * 60 * 24 * 7 + 60 + 60 * 60,
            'local_id': '6fc2c510:charlie',
            'location': 'Charlie Venue, Rest of Charlie Location',
            'start': 60 * 60 * 24 * 7 + 60,
            'summary': 'Charlie Summary',
        },
    }

    conv = build_conversation(events, moderator)
    conv.multibot.multical.add('static:test_events')
    conv.multibot.calendars['6fc2c510'] = {'name': 'Test Calendar'}
    return conv


# pylint: disable=line-too-long


def test_generate_preamble():  # pylint: disable=missing-docstring
    # yapf: disable - pylint: disable=protected-access
    assert reminders._generate_preamble('', []) == (
        'No upcoming events!')
    assert reminders._generate_preamble('1 + 1 = 2!', []) == (
        '1 + 1 = 2!')

    assert reminders._generate_preamble('', ['EVENT1']) == (
        "There's an event coming up:")
    assert reminders._generate_preamble('', ['EVENT1', 'EVENT2']) == (
        "There are a couple events coming up:")
    assert reminders._generate_preamble('', ['EVENT1', 'EVENT2', 'EVENT3']) == (
        "There are a few events coming up:")
    assert reminders._generate_preamble('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4']) == (
        "There are a bunch of events coming up:")
    assert reminders._generate_preamble('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4', 'EVENT5']) == (
        "There are a bunch of events coming up:")

    assert reminders._generate_preamble('1 + 1 = 2!', ['EVENT1']) == (
        "1 + 1 = 2! Also, there's an event coming up:")

    assert reminders._generate_preamble('Visit @MYGROUP', ['EVENT1']) == (
        "Visit @MYGROUP • Also, there's an event coming up:")

    assert reminders._generate_preamble('I love events.', ['EVENT1']) == (
        "I love events. Speaking of which, there's an event coming up:")

    assert reminders._generate_preamble('I love events:', ['EVENT1']) == (
        "I love events:")
    # yapf: enable


@pytest.fixture
def daily_messages(conversation):  # pylint: disable=missing-docstring,redefined-outer-name
    replies = conversation.raw_message('/dummy')
    assert conversation.format_messages(replies) == ''

    records = {}

    def _daily_messages(initial=False):
        replies.clear()
        if initial:
            records.clear()
            conversation.bot.config['issue37']['moderator']['-1002000002000']['daily']['hour'] = 0
        else:
            conversation.bot.config['issue37']['moderator']['-1002000002000']['daily']['hour'] = 1
        reminders._daily_messages(conversation.multibot, records)  # pylint: disable=protected-access
        outrecords = {'/'.join(key): record for key, record in records.items()}
        text = outrecords and yaml.safe_dump(outrecords, width=float('inf'),
                                             allow_unicode=True) or ''
        text = text.replace('\n\n', '\n')
        text = f'{text}\n\n{conversation.format_messages(replies)}'.strip()
        if text:
            text = f'\n{text}\n'
        return text

    assert _daily_messages(True) == ''

    conversation.bot.config['issue37']['moderator']['-1002000002000'] = {
        'calendars': '6fc2c510',
        'daily': {
            'hour': 0,
        },
        'timezone': 'UTC',
    }

    return _daily_messages


def test_daily_messages(daily_messages):  # pylint: disable=redefined-outer-name
    """Test basic daily announcement logic (essentially, test the daily_messages fixture)."""

    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''
"""


def test_daily_messages_updated(daily_messages):  # pylint: disable=redefined-outer-name
    """Test daily announcement update messages."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['summary'] = 'Edited Summary'
    cal.events['6fc2c510:alpha']['end'] += 60

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12660.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Edited Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Edited Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• <s>Alpha Summary</s> is now called <b>Edited Summary</b> and was extended to <b>Thu 1ˢᵗ, 3:31ᵃᵐ</b> (instead of <s>Thu 1ˢᵗ, 3:30ᵃᵐ</s>).


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12660.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Edited Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Edited Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>
"""


def test_daily_messages_future(daily_messages, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test the behavior when an event transitions from TODAY to NOW."""

    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    # See https://github.com/nmlorg/metabot/issues/97.
    monkeypatch.setattr('time.time', lambda: 60 * 60 * 2.5)

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['summary'] = 'Now Summary'

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Now Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Now Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 2:30ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• <s>Alpha Summary</s> is now called <b>Now Summary</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Now Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 2:30ᵃᵐ</a>]
"""


def test_daily_messages_multiline(daily_messages):  # pylint: disable=redefined-outer-name
    """Verify multiline event components are rendered in updates concisely."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['description'] = 'Multi\n\nLine\nDescription'

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: 'Multi

      Line
      Description'
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• The description of <b>Alpha Summary</b> was changed from <s>Alpha Description</s> to <b>Multi Line Description</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""


def test_daily_messages_add_remove_event(conversation, daily_messages):  # pylint: disable=redefined-outer-name
    """Verify what happens when events are added/removed entirely."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:new'] = {
        'description': 'New Description',
        'end': 60 * 60 * 4.5,
        'local_id': '6fc2c510:new',
        'location': 'New Venue, Rest of New Location',
        'start': 60 * 60 * 3.5,
        'summary': 'New Summary',
    }
    conversation.multibot.multical.ordered.append(cal.events['6fc2c510:new'])
    cal.events.pop('6fc2c510:bravo')
    assert conversation.multibot.multical.ordered[1]['local_id'] == '6fc2c510:bravo'
    assert conversation.multibot.multical.ordered.pop(1)
    conversation.multibot.multical._rebuild()  # pylint: disable=protected-access

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: New Description
    end: 16200.0
    local_id: 6fc2c510:new
    location: New Venue, Rest of New Location
    start: 12600.0
    summary: New Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>New Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 3:30–4:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• <b>New Summary</b> was added.
• <s>Bravo Summary</s> was removed.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>New Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 3:30–4:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""


def test_daily_messages_ignored(daily_messages):  # pylint: disable=redefined-outer-name
    """Verify non-notification-worthy changes are properly ignored."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['description'] = (
        'Alpha Description https://www.example.com/?id=1234')

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''
"""

    cal.events['6fc2c510:alpha']['updated'] = 23456

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''
"""


def test_daily_messages_icons(conversation, daily_messages):  # pylint: disable=redefined-outer-name
    """Run through all the cases where events trigger banner images."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['description'] = 'Board Games!'

    # An update does not include references to icons.
    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Board Games!
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• The description of <b>Alpha Summary</b> was changed from <s>Alpha Description</s> to <b>Board Games!</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""

    # But an initial announcement does (photo=...).
    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Board Games!
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- caption: CAPTION
  chat:
    id: -1002000002000
  message_id: 12347
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[send_media_group chat_id=-1002000002000 disable_notification=True media=[[media=https://ssl.gstatic.com/calendar/images/eventillustrations/v1/img_gamenight_2x.jpg parse_mode=HTML type=photo]]]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    conversation.bot.config['issue37']['events']['series']['ha sum'] = 'SERIES ICON'

    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Board Games!
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- caption: CAPTION
  chat:
    id: -1002000002000
  message_id: 12348
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[send_media_group chat_id=-1002000002000 disable_notification=True media=[[media=SERIES ICON parse_mode=HTML type=photo]]]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    conversation.bot.config['issue37']['events']['events']['6fc2c510:alpha'] = 'ALPHA ICON'
    conversation.bot.config['issue37']['events']['events']['6fc2c510:bravo'] = 'BRAVO ICON'

    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Board Games!
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- caption: CAPTION
  chat:
    id: -1002000002000
  message_id: 12349
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[send_media_group chat_id=-1002000002000 disable_notification=True media=[[media=ALPHA ICON parse_mode=HTML type=photo] [media=BRAVO ICON type=photo]]]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    cal.events['6fc2c510:alpha']['description'] = 'Fun Games!'
    conversation.bot.config['issue37']['events']['events']['6fc2c510:alpha'] = None
    conversation.bot.config['issue37']['events']['events']['6fc2c510:bravo'] = None

    # Removing an icon trigger leaves the image in place.
    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Fun Games!
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- caption: CAPTION
  chat:
    id: -1002000002000
  message_id: 12349
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12351">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12349]
Updated:
• The description of <b>Alpha Summary</b> was changed from <s>Board Games!</s> to <b>Fun Games!</b>.


[edit_message_caption chat_id=-1002000002000 message_id=12349 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12351">Updated 12:33ᵃᵐ</a>]
"""


def test_daily_messages_geometry(conversation, daily_messages):  # pylint: disable=redefined-outer-name
    """See https://github.com/nmlorg/metabot/issues/75."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['description'] = 'Trigger'
    conversation.bot.config['issue37']['moderator']['-1002000002000']['maxeventscount'] = 1

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Trigger
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There''s an event coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• The description of <b>Alpha Summary</b> was changed from <s>Alpha Description</s> to <b>Trigger</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There's an event coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""


def test_daily_messages_grammar(daily_messages):  # pylint: disable=redefined-outer-name
    """Quick tests for the differ's grammar."""

    daily_messages(True)
    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['summary'] = 'New Summary'
    cal.events['6fc2c510:alpha']['start'] -= 1800
    cal.events['6fc2c510:alpha']['location'] = 'New Location'
    cal.events['6fc2c510:alpha']['description'] = 'New Description'
    cal.events['6fc2c510:bravo']['start'] -= 1800
    cal.events['6fc2c510:bravo']['end'] += 1800
    cal.events['6fc2c510:bravo']['location'] = 'New Location'
    cal.events['6fc2c510:bravo']['description'] = 'New Description'

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: New Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: New Location
    start: 7200.0
    summary: New Summary
  - description: New Description
    end: 610200
    local_id: 6fc2c510:bravo
    location: New Location
    start: 603000
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>New Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ¹ʰ³⁰ᵐ Thu 1ˢᵗ, 2–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Location">New Location</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁶ ᵈᵃʸˢ Wed 7ᵗʰ, 11:30ᵖᵐ – 1:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Location">New Location</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• <s>Alpha Summary</s> is now called <b>New Summary</b>, is starting earlier at <b>Thu 1ˢᵗ, 2ᵃᵐ</b> (instead of <s>Thu 1ˢᵗ, 2:30ᵃᵐ</s>; same end), was moved from <s>Alpha Venue</s> to <b>New Location</b>, and its description was changed from <s>Alpha Description</s> to <b>New Description</b>.
• <b>Bravo Summary</b> now starts at <b>Wed 7ᵗʰ, 11:30ᵖᵐ</b> and ends at <b>Thu 8ᵗʰ, 1:30ᵃᵐ</b> (was <s>Thu 8ᵗʰ, 12ᵃᵐ to Thu 8ᵗʰ, 1ᵃᵐ</s>), was moved from <s>Bravo Venue</s> to <b>New Location</b>, and its description was changed from <s>Bravo Description</s> to <b>New Description</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>New Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ¹ʰ³⁰ᵐ Thu 1ˢᵗ, 2–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Location">New Location</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁶ ᵈᵃʸˢ Wed 7ᵗʰ, 11:30ᵖᵐ – 1:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Location">New Location</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""


def test_daily_messages_replaced(conversation, daily_messages, monkeypatch):  # pylint: disable=redefined-outer-name
    """Test what happens when an existing announcement is obsoleted the next day."""

    monkeypatch.setattr('time.time', lambda: 4000)

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 3600
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ¹ʰ³⁰ᵐ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ¹ʰ³⁰ᵐ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>
"""

    monkeypatch.setattr('time.time', lambda: 4000 + 60 * 60 * 24)

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 90000
- - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
  - description: Charlie Description
    end: 608460
    local_id: 6fc2c510:charlie
    location: Charlie Venue, Rest of Charlie Location
    start: 604860
    summary: Charlie Summary
- chat:
    id: -1002000002000
  message_id: 12346
- 'There are a couple events coming up:

  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁶ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
  <b>Charlie Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁶ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁶ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
<b>Charlie Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁶ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""

    conversation.bot.config['issue37']['moderator']['-1002000002000']['daily']['pin'] = True
    monkeypatch.setattr('time.time', lambda: 4000 + 60 * 60 * 24 * 2)

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 176400
- - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
  - description: Charlie Description
    end: 608460
    local_id: 6fc2c510:charlie
    location: Charlie Venue, Rest of Charlie Location
    start: 604860
    summary: Charlie Summary
- chat:
    id: -1002000002000
  message_id: 12347
  pinned: true
- 'There are a couple events coming up:

  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁵ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
  <b>Charlie Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁵ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁵ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
<b>Charlie Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁵ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>


[pin_chat_message chat_id=-1002000002000 disable_notification=True message_id=12347]
(EMPTY MESSAGE)


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12346 parse_mode=HTML]
There are a couple events coming up:

<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
<b>Charlie Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>
"""

    monkeypatch.setattr('time.time', lambda: 4000 + 60 * 60 * 24 * 3)

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 262800
- - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
  - description: Charlie Description
    end: 608460
    local_id: 6fc2c510:charlie
    location: Charlie Venue, Rest of Charlie Location
    start: 604860
    summary: Charlie Summary
- chat:
    id: -1002000002000
  message_id: 12349
  pinned: true
- 'There are a couple events coming up:

  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁴ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
  <b>Charlie Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁴ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">⁴ ᵈᵃʸˢ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
<b>Charlie Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">⁴ ᵈᵃʸˢ Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>


[pin_chat_message chat_id=-1002000002000 disable_notification=True message_id=12349]
(EMPTY MESSAGE)


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12347 parse_mode=HTML]
There are a couple events coming up:

<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
<b>Charlie Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpjaGFybGllIFVUQw">Thu 8ᵗʰ, 12:01–1:01ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Charlie+Venue%2C+Rest+of+Charlie+Location">Charlie Venue</a>


[unpin_chat_message chat_id=-1002000002000 message_id=12347]
(EMPTY MESSAGE)
"""


def test_diff_time():
    """Test start/end time difference detector."""

    tzinfo = pytz.timezone('America/Los_Angeles')
    base = datetime.datetime.fromtimestamp(1719946200, tzinfo)
    start = 1719946800.
    end = 1719950400

    # pylint: disable=protected-access

    assert not reminders._diff_time(start, end, start, end, tzinfo, base)

    assert reminders._diff_time(start, end, start + 60, end + 120, tzinfo, base) == (
        'now starts at <b>Tue 2ⁿᵈ, 12:01ᵖᵐ</b> and ends at <b>Tue 2ⁿᵈ, 1:02ᵖᵐ</b> (was <s>Tue 2ⁿᵈ, 12ᵖᵐ to Tue 2ⁿᵈ, 1ᵖᵐ</s>)'
    )

    assert reminders._diff_time(start, end, start - 60, end, tzinfo, base) == (
        'is starting earlier at <b>Tue 2ⁿᵈ, 11:59ᵃᵐ</b> (instead of <s>Tue 2ⁿᵈ, 12ᵖᵐ</s>; same end)'
    )
    assert reminders._diff_time(start, end, start - 60, end - 60, tzinfo, base) == (
        'was moved up to <b>Tue 2ⁿᵈ, 11:59ᵃᵐ</b> (from <s>Tue 2ⁿᵈ, 12ᵖᵐ</s>; same duration)')

    assert reminders._diff_time(start, end, start + 60, end, tzinfo, base) == (
        'is starting later at <b>Tue 2ⁿᵈ, 12:01ᵖᵐ</b> (instead of <s>Tue 2ⁿᵈ, 12ᵖᵐ</s>; same end)')
    assert reminders._diff_time(start, end, start + 60, end + 60, tzinfo, base) == (
        'was moved back to <b>Tue 2ⁿᵈ, 12:01ᵖᵐ</b> (from <s>Tue 2ⁿᵈ, 12ᵖᵐ</s>; same duration)')

    assert reminders._diff_time(
        start, end, start, end - 60, tzinfo,
        base) == ('was shortened to <b>Tue 2ⁿᵈ, 12:59ᵖᵐ</b> (instead of <s>Tue 2ⁿᵈ, 1ᵖᵐ</s>)')
    assert reminders._diff_time(
        start, end, start, end + 60, tzinfo,
        base) == ('was extended to <b>Tue 2ⁿᵈ, 1:01ᵖᵐ</b> (instead of <s>Tue 2ⁿᵈ, 1ᵖᵐ</s>)')


def test_quick_diff():
    """Test description string differ."""

    # pylint: disable=protected-access
    assert reminders._quick_diff('', '') is None
    assert reminders._quick_diff('0987654321', '0987654321new') == ('0987654321', '0987654321new')
    assert reminders._quick_diff('10987654321', '10987654321new') == ('…987654321', '…987654321new')
    assert reminders._quick_diff('10987654321old', '10987654321') == ('…987654321old', '…987654321')
    assert reminders._quick_diff('10987654321old',
                                 '10987654321new') == ('…987654321old', '…987654321new')
    assert reminders._quick_diff(
        'x',
        'x234567890123456789012345678901234567890') == ('x',
                                                        'x234567890123456789012345678901234567890')
    assert reminders._quick_diff(
        'x',
        'x2345678901234567890123456789012345678901') == ('x',
                                                         'x23456789012345678901234567890123456789…')


def test_truncation(daily_messages, monkeypatch):  # pylint: disable=redefined-outer-name
    """Verify that message limits are correctly enforced."""

    monkeypatch.setattr('ntelebot.limits.message_text_length_max', 40)

    assert daily_messages(True) == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Alpha Venue, Rest of Alpha Location
    start: 9000.0
    summary: Alpha Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Al</b>
"""
    assert len('There are a couple events coming up:\n\nAl') == 40


def test_sanitize(daily_messages):  # pylint: disable=redefined-outer-name
    """Verify entity escaping."""

    daily_messages(True)

    cal = loader.get('static:test_events')
    cal.events['6fc2c510:alpha']['summary'] = 'Edited & <i> Summary'
    cal.events['6fc2c510:alpha']['location'] = 'Edited & <i> Location, Rest of Location'

    assert daily_messages() == """
modulestestbot/-1002000002000:
- 1800
- - description: Alpha Description
    end: 12600.0
    local_id: 6fc2c510:alpha
    location: Edited & <i> Location, Rest of Location
    start: 9000.0
    summary: Edited & <i> Summary
  - description: Bravo Description
    end: 608400
    local_id: 6fc2c510:bravo
    location: Bravo Venue, Rest of Bravo Location
    start: 604800
    summary: Bravo Summary
- chat:
    id: -1002000002000
  message_id: 12345
- 'There are a couple events coming up:

  <b>Edited &amp; &lt;i&gt; Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Edited+%26+%3Ci%3E+Location%2C+Rest+of+Location">Edited &amp; &lt;i&gt; Location</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

  <i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>'
- <a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
• <s>Alpha Summary</s> is now called <b>Edited &amp; &lt;i&gt; Summary</b> and was moved from <s>Alpha Venue</s> to <b>Edited &amp; &lt;i&gt; Location</b>.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Edited &amp; &lt;i&gt; Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Edited+%26+%3Ci%3E+Location%2C+Rest+of+Location">Edited &amp; &lt;i&gt; Location</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

<i>Click the date/time for more details or to RSVP, or the location to pop open a map.</i>

[<a href="https://t.me/c/2000002000/12346">Updated 12:33ᵃᵐ</a>]
"""
