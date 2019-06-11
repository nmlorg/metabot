"""Tests for metabot.util.adminui."""

import pytest

from metabot.modules import echo
from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    conv = build_conversation(echo, moderator)
    conv.groupconf = conv.multibot.conf['bots']['modulestestbot']['issue37']['moderator'][
        '-1001000001000']
    conv.groupconf['title'] = 'Test Group'
    return conv


# pylint: disable=line-too-long


def test_bool(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.bool."""

    echoconf = conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['dummy']

    assert 'paginate' not in echoconf

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Enabled <code>paginate</code>.
[text • The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[paginate (yes) • For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[Back | /admin modulestestbot echo]
"""

    assert echoconf['paginate'] is True

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Disabled <code>paginate</code>.
[text • The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[paginate (no) • For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[Back | /admin modulestestbot echo]
"""

    assert 'paginate' not in echoconf


def test_daysofweek(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.daysofweek."""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 dailydow') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>enabled</b>.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [disable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [disable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [disable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[disable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [disable every day | /admin modulestestbot moderator -1001000001000 dailydow none]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert 'dailydow' not in conversation.groupconf

    assert conversation.message('none') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>disabled</b>.

Select a day of the week to toggle:
[enable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[enable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [enable every day | /admin modulestestbot moderator -1001000001000 dailydow all]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['dailydow'] == 127

    assert conversation.message('1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Tuesday.

Select a day of the week to toggle:
[enable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [enable every day | /admin modulestestbot moderator -1001000001000 dailydow all]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['dailydow'] == 125

    assert conversation.message('6') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Sunday and Tuesday.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [enable every day | /admin modulestestbot moderator -1001000001000 dailydow all]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['dailydow'] == 61

    assert conversation.message('3') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Sunday, Tuesday, and Thursday.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [enable every day | /admin modulestestbot moderator -1001000001000 dailydow all]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['dailydow'] == 53

    assert conversation.message('all') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › dailydow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>enabled</b>.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 dailydow 6] [disable Monday | /admin modulestestbot moderator -1001000001000 dailydow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 dailydow 1] [disable Wednesday | /admin modulestestbot moderator -1001000001000 dailydow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 dailydow 3] [disable Friday | /admin modulestestbot moderator -1001000001000 dailydow 4]
[disable Saturday | /admin modulestestbot moderator -1001000001000 dailydow 5] [disable every day | /admin modulestestbot moderator -1001000001000 dailydow none]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert 'dailydow' not in conversation.groupconf


def test_forward(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.forward."""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['moderator']['-1002000002000'][
        'title'] = 'Forward Source'

    assert conversation.message('/admin modulestestbot moderator -1001000001000 forward') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › forward: <b>Choose a field</b>

Automatically forward messages from one chat to this one.
[from • What group should messages be forwarded from? | /admin modulestestbot moderator -1001000001000 forward from]
[notify (no) • Should forwarded messages trigger a notification? | /admin modulestestbot moderator -1001000001000 forward notify]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 forward from') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › forward › from: <b>Select a group</b>

Automatically forward messages from one chat to this one.

What group should messages be forwarded from?

Select a group:
[-1001000001000 (Test Group) | /admin modulestestbot moderator -1001000001000 forward from -1001000001000]
[-1002000002000 (Forward Source) | /admin modulestestbot moderator -1001000001000 forward from -1002000002000]
[Back | /admin modulestestbot moderator -1001000001000 forward]
"""

    assert conversation.message('-1002000002000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › forward: <b>Choose a field</b>

Automatically forward messages from one chat to this one.

Set <code>from</code> to <code>-1002000002000</code>.
[from (-10020000…) • What group should messages be forwarded from? | /admin modulestestbot moderator -1001000001000 forward from]
[notify (no) • Should forwarded messages trigger a notification? | /admin modulestestbot moderator -1001000001000 forward notify]
[Back | /admin modulestestbot moderator -1001000001000]
"""


def test_integer(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.integer."""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Type a new value for daily</b>

Should I announce upcoming events once a day? If so, at what hour?

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert 'daily' not in conversation.groupconf

    assert conversation.message('8') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Set <code>daily</code> to <code>8</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily (8) • Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailydow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 dailydow]
[dailytext • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.groupconf['daily'] == 8

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Type a new value for daily</b>

Should I announce upcoming events once a day? If so, at what hour?

<code>daily</code> is currently <code>8</code>.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('9') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Changed <code>daily</code> from <code>8</code> to <code>9</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily (9) • Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailydow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 dailydow]
[dailytext • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.groupconf['daily'] == 9

    assert conversation.message('daily off') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Unset <code>daily</code> (was <code>9</code>).
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailydow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 dailydow]
[dailytext • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert 'daily' not in conversation.groupconf

    assert conversation.message('daily off') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

<code>daily</code> is already unset.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? If so, at what hour? | /admin modulestestbot moderator -1001000001000 daily]
[dailydow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 dailydow]
[dailytext • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 dailytext]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""
