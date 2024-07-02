"""Tests for metabot.modules.reminders."""

import pytest
import yaml

from metabot.calendars import loader
from metabot.modules import events
from metabot.modules import moderator
from metabot.modules import reminders


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


def test_format_daily_message():  # pylint: disable=missing-docstring
    # yapf: disable - pylint: disable=protected-access
    assert reminders._format_daily_message('', []) == (
        'No upcoming events!')
    assert reminders._format_daily_message('1 + 1 = 2!', []) == (
        '1 + 1 = 2!')

    assert reminders._format_daily_message('', ['EVENT1']) == (
        "There's an event coming up:\n"
        '\n'
        'EVENT1')
    assert reminders._format_daily_message('', ['EVENT1', 'EVENT2']) == (
        "There are a couple events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2')
    assert reminders._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3']) == (
        "There are a few events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3')
    assert reminders._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4']) == (
        "There are a bunch of events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3\n'
        'EVENT4')
    assert reminders._format_daily_message('', ['EVENT1', 'EVENT2', 'EVENT3', 'EVENT4', 'EVENT5']) == (
        "There are a bunch of events coming up:\n"
        '\n'
        'EVENT1\n'
        'EVENT2\n'
        'EVENT3\n'
        'EVENT4\n'
        'EVENT5')

    assert reminders._format_daily_message('1 + 1 = 2!', ['EVENT1']) == (
        "1 + 1 = 2! Also, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert reminders._format_daily_message('Visit @MYGROUP', ['EVENT1']) == (
        "Visit @MYGROUP • Also, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert reminders._format_daily_message('I love events.', ['EVENT1']) == (
        "I love events. Speaking of which, there's an event coming up:\n"
        '\n'
        'EVENT1')

    assert reminders._format_daily_message('I love events:', ['EVENT1']) == (
        "I love events:\n"
        '\n'
        'EVENT1')
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Edited Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Edited Summary
      <s>Alpha Summary</s>
      Edited Summary
      <s>… 2:30–3:30ᵃᵐ</s>
      … 2:30–3:31ᵃᵐ


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Edited Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Edited Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:31ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Now Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 2:30ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Now Summary
      <s>Alpha Summary</s>
      Now Summary


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Now Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">⭐ ᴺᴼᵂ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 2:30ᵃᵐ</a>]
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Alpha Summary
      <s>Alpha Description</s>
      Multi Line Description


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>New Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 3:30–4:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • New Summary
    ◦ New event!
  • Bravo Summary
    ◦ Removed.


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>New Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpuZXcgVVRD">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 3:30–4:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=New+Venue%2C+Rest+of+New+Location">New Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
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
- message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Alpha Summary
      <s>Alpha Description</s>
      Board Games!


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
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
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[send_photo chat_id=-1002000002000 disable_notification=True parse_mode=HTML photo=https://ssl.gstatic.com/calendar/images/eventillustrations/v1/img_gamenight_2x.jpg]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
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
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[send_photo chat_id=-1002000002000 disable_notification=True parse_mode=HTML photo=SERIES ICON]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""

    conversation.bot.config['issue37']['events']['events']['6fc2c510:alpha'] = 'EVENT ICON'

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
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- ''


[send_photo chat_id=-1002000002000 disable_notification=True parse_mode=HTML photo=EVENT ICON]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>
"""

    cal.events['6fc2c510:alpha']['description'] = 'Fun Games!'

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
  message_id: 12345
- 'There are a couple events coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
  <b>Bravo Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Alpha Summary
      <s>Board Games!</s>
      Fun Games!


[edit_message_caption chat_id=-1002000002000 message_id=12345 parse_mode=HTML]
There are a couple events coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>
<b>Bravo Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDpicmF2byBVVEM">¹ʷ Thu 8ᵗʰ, 12–1ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Bravo+Venue%2C+Rest+of+Bravo+Location">Bravo Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
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
- message_id: 12345
- 'There''s an event coming up:

  <b>Alpha Summary</b>
  <a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>'
- <a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>


[chat_id=-1002000002000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
Updated:
  • Alpha Summary
      <s>Alpha Description</s>
      Trigger


[edit_message_text chat_id=-1002000002000 disable_web_page_preview=True message_id=12345 parse_mode=HTML]
There's an event coming up:

<b>Alpha Summary</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyA2ZmMyYzUxMDphbHBoYSBVVEM">🔜 ² ʰᵒᵘʳˢ Thu 1ˢᵗ, 2:30–3:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

[<a href="https://t.me/c/2000002000/12345">Updated 12:33ᵃᵐ</a>]
"""


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


@pytest.fixture
def handle_alerts(conversation):  # pylint: disable=missing-docstring,redefined-outer-name
    replies = conversation.raw_message('/dummy')
    assert conversation.format_messages(replies) == ''

    records = {}
    groupid = '-1001000001000'

    def _handle_alerts(alerts):
        replies.clear()
        reminders._handle_alerts(conversation.bot, records, groupid, alerts)  # pylint: disable=protected-access
        return conversation.format_messages(replies)

    return _handle_alerts


def test_handle_alerts(handle_alerts):  # pylint: disable=redefined-outer-name
    """Test basic behavior of reminders._handle_alerts."""

    # First poll; no active alerts.
    assert handle_alerts([]) == ''

    # Second poll; brand-new alert.
    alerts = [{
        'id': 'alert-id',
        'areaDesc': 'Area description',
        'description': 'Alert Description',
        'instruction': 'Alert Instructions',
        'event': 'Winter Storm Warning',
        'messageType': 'Alert',
        'urgency': 'Immediate',
        'severity': 'Extreme',
        'certainty': 'Observed',
    }]
    assert handle_alerts(alerts) == """\
[chat_id=-1001000001000 disable_notification=True disable_web_page_preview=True parse_mode=HTML]
<a href="https://alerts-v2.weather.gov/products/alert-id">Winter Storm Warning alert-id</a>

Alert Description

Alert Instructions

Area description
"""

    # Third poll; same alert is active.
    assert handle_alerts(alerts) == ''

    # Fourth poll; existing alert is modified.
    alerts[0]['instruction'] = 'Run for your lives!'
    assert handle_alerts(alerts) == """\
[chat_id=-1001000001000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
<a href="https://alerts-v2.weather.gov/products/alert-id">Winter Storm Warning alert-id</a>

Alert Description

Run for your lives!

Area description
"""

    # Fifth poll; another new alert.
    alerts.append({
        'id': 'alert-id-2',
        'areaDesc': 'Second area description',
        'description': 'Second Description',
        'instruction': 'Second Instructions',
        'event': 'Winter Storm Watch',
        'messageType': 'Alert',
        'urgency': 'Immediate',
        'severity': 'Extreme',
        'certainty': 'Observed',
    })
    assert handle_alerts(alerts) == """\
[chat_id=-1001000001000 disable_notification=True disable_web_page_preview=True parse_mode=HTML reply_to_message_id=12345]
<a href="https://alerts-v2.weather.gov/products/alert-id">Winter Storm Warning alert-id</a>

Alert Description

Run for your lives!

Area description


<a href="https://alerts-v2.weather.gov/products/alert-id-2">Winter Storm Watch alert-id-2</a>

Second Description

Second Instructions

Second area description
"""

    # Sixth poll; both alerts have been canceled.
    assert handle_alerts([]) == ''

    # Seventh poll; a new alert that we don't care about.
    alerts = [{
        'id': 'alert-id-3',
        'areaDesc': 'Third area description',
        'description': 'Third Description',
        'instruction': 'Third Instructions',
        'event': 'Special Weather Statement',
        'messageType': 'Alert',
        'urgency': 'Immediate',
        'severity': 'Moderate',
        'certainty': 'Observed',
    }]
    assert handle_alerts([]) == ''
