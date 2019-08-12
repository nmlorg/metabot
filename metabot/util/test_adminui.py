"""Tests for metabot.util.adminui."""

import pytest

from metabot.modules import echo
from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    conv = build_conversation(echo, moderator)
    conv.groupconf = conv.bot.config['issue37']['moderator']['-1001000001000']
    conv.groupconf['title'] = 'Test Group'
    return conv


# pylint: disable=line-too-long


def test_bool(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.bool."""

    echoconf = conversation.bot.config['issue37']['echo']['dummy']

    assert 'paginate' not in echoconf

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Enabled <code>paginate</code>.
[paginate (yes) • For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[text • The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[Back | /admin modulestestbot echo]
"""

    assert echoconf['paginate'] is True

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Disabled <code>paginate</code>.
[paginate (no) • For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[text • The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[Back | /admin modulestestbot echo]
"""

    assert 'paginate' not in echoconf


def test_daysofweek(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.daysofweek."""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily dow') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>enabled</b>.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [disable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [disable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [disable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[disable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [disable every day | /admin modulestestbot moderator -1001000001000 daily dow none]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert 'daily' not in conversation.groupconf

    assert conversation.message('none') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>disabled</b>.

Select a day of the week to toggle:
[enable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[enable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [enable every day | /admin modulestestbot moderator -1001000001000 daily dow all]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert conversation.groupconf['daily'] == {'dow': 127}

    assert conversation.message('1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Tuesday.

Select a day of the week to toggle:
[enable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [enable every day | /admin modulestestbot moderator -1001000001000 daily dow all]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert conversation.groupconf['daily'] == {'dow': 125}

    assert conversation.message('6') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Sunday and Tuesday.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[enable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [enable every day | /admin modulestestbot moderator -1001000001000 daily dow all]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert conversation.groupconf['daily'] == {'dow': 61}

    assert conversation.message('3') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

Enabled for Sunday, Tuesday, and Thursday.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [enable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [enable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [enable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[enable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [enable every day | /admin modulestestbot moderator -1001000001000 daily dow all]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert conversation.groupconf['daily'] == {'dow': 53}

    assert conversation.message('all') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › dow: <b>Select a day of the week to toggle</b>

Which days of the week should I announce upcoming events on?

All days are currently <b>enabled</b>.

Select a day of the week to toggle:
[disable Sunday | /admin modulestestbot moderator -1001000001000 daily dow 6] [disable Monday | /admin modulestestbot moderator -1001000001000 daily dow 0]
[disable Tuesday | /admin modulestestbot moderator -1001000001000 daily dow 1] [disable Wednesday | /admin modulestestbot moderator -1001000001000 daily dow 2]
[disable Thursday | /admin modulestestbot moderator -1001000001000 daily dow 3] [disable Friday | /admin modulestestbot moderator -1001000001000 daily dow 4]
[disable Saturday | /admin modulestestbot moderator -1001000001000 daily dow 5] [disable every day | /admin modulestestbot moderator -1001000001000 daily dow none]
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert 'daily' not in conversation.groupconf


def test_forward(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.forward."""

    conversation.bot.config['issue37']['moderator']['-1002000002000']['title'] = 'Forward Source'

    assert conversation.message('/admin modulestestbot moderator -1001000001000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

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

What group should messages be forwarded from?

Select a group:
[-1001000001000 (Test Group) | /admin modulestestbot moderator -1001000001000 forward from -1001000001000]
[-1002000002000 (Forward Source) | /admin modulestestbot moderator -1001000001000 forward from -1002000002000]
[Back | /admin modulestestbot moderator -1001000001000 forward]
"""

    assert conversation.message('-1002000002000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › forward: <b>Choose a field</b>

Set <code>from</code> to <code>-1002000002000</code>.

Automatically forward messages from one chat to this one.
[from (-10020000…) • What group should messages be forwarded from? | /admin modulestestbot moderator -1001000001000 forward from]
[notify (no) • Should forwarded messages trigger a notification? | /admin modulestestbot moderator -1001000001000 forward notify]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""


def test_integer(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.integer."""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Choose a field</b>

Should I announce upcoming events once a day?
[dow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 daily dow]
[hour • At what hour? | /admin modulestestbot moderator -1001000001000 daily hour]
[text • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 daily text]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily hour') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › hour: <b>Type a new value for hour</b>

At what hour?

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert 'daily' not in conversation.groupconf

    assert conversation.message('8') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Choose a field</b>

Set <code>hour</code> to <code>8</code>.

Should I announce upcoming events once a day?
[dow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 daily dow]
[hour (8) • At what hour? | /admin modulestestbot moderator -1001000001000 daily hour]
[text • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 daily text]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['daily'] == {'hour': 8}

    assert conversation.message('/admin modulestestbot moderator -1001000001000 daily hour') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily › hour: <b>Type a new value for hour</b>

At what hour?

<code>hour</code> is currently <code>8</code>.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000 daily]
"""

    assert conversation.message('9') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Choose a field</b>

Changed <code>hour</code> from <code>8</code> to <code>9</code>.

Should I announce upcoming events once a day?
[dow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 daily dow]
[hour (9) • At what hour? | /admin modulestestbot moderator -1001000001000 daily hour]
[text • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 daily text]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.groupconf['daily'] == {'hour': 9}

    assert conversation.message('hour off') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Choose a field</b>

Unset <code>hour</code> (was <code>9</code>).

Should I announce upcoming events once a day?
[dow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 daily dow]
[hour • At what hour? | /admin modulestestbot moderator -1001000001000 daily hour]
[text • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 daily text]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert 'daily' not in conversation.groupconf

    assert conversation.message('hour off') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › daily: <b>Choose a field</b>

<code>hour</code> is already unset.

Should I announce upcoming events once a day?
[dow • Which days of the week should I announce upcoming events on? | /admin modulestestbot moderator -1001000001000 daily dow]
[hour • At what hour? | /admin modulestestbot moderator -1001000001000 daily hour]
[text • One or more messages (one per line) to use/cycle through for the daily announcement. | /admin modulestestbot moderator -1001000001000 daily text]
[Back | /admin modulestestbot moderator -1001000001000]
"""


def test_timezone(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.timezone."""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 timezone') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Type your 2-letter country code</b>

Type your 2-letter country code (like US, CA, GB, etc.).
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone dummy') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Type your 2-letter country code</b>

Unknown country code <code>DUMMY</code>.

Type your 2-letter country code (like US, CA, GB, etc.).
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone gb') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[London | /admin modulestestbot moderator -1001000001000 timezone Europe/London]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone us') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[New York (Eastern (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/New_York]
[Detroit (Eastern - MI (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/Detroit]
[Louisville (Eastern - KY (Louisville area)) | /admin modulestestbot moderator -1001000001000 timezone America/Kentucky/Louisville]
[Monticello (Eastern - KY (Wayne)) | /admin modulestestbot moderator -1001000001000 timezone America/Kentucky/Monticello]
[Indianapolis (Eastern - IN (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Indianapolis]
[Vincennes (Eastern - IN (Da, Du, K, Mn)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vincennes]
[Winamac (Eastern - IN (Pulaski)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Winamac]
[\xa0 | /stop] [Next | /admin modulestestbot moderator -1001000001000 timezone US 1]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone US 1') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[Marengo (Eastern - IN (Crawford)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Marengo]
[Petersburg (Eastern - IN (Pike)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Petersburg]
[Vevay (Eastern - IN (Switzerland)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Vevay]
[Chicago (Central (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/Chicago]
[Tell City (Central - IN (Perry)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Tell_City]
[Knox (Central - IN (Starke)) | /admin modulestestbot moderator -1001000001000 timezone America/Indiana/Knox]
[Menominee (Central - MI (Wisconsin border)) | /admin modulestestbot moderator -1001000001000 timezone America/Menominee]
[Prev | /admin modulestestbot moderator -1001000001000 timezone US 0] [Next | /admin modulestestbot moderator -1001000001000 timezone US 2]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone US 2') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[Center (Central - ND (Oliver)) | /admin modulestestbot moderator -1001000001000 timezone America/North_Dakota/Center]
[New Salem (Central - ND (Morton rural)) | /admin modulestestbot moderator -1001000001000 timezone America/North_Dakota/New_Salem]
[Beulah (Central - ND (Mercer)) | /admin modulestestbot moderator -1001000001000 timezone America/North_Dakota/Beulah]
[Denver (Mountain (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/Denver]
[Boise (Mountain - ID (south); OR (east)) | /admin modulestestbot moderator -1001000001000 timezone America/Boise]
[Phoenix (MST - Arizona (except Navajo)) | /admin modulestestbot moderator -1001000001000 timezone America/Phoenix]
[Los Angeles (Pacific) | /admin modulestestbot moderator -1001000001000 timezone America/Los_Angeles]
[Prev | /admin modulestestbot moderator -1001000001000 timezone US 1] [Next | /admin modulestestbot moderator -1001000001000 timezone US 3]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone US 3') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[Anchorage (Alaska (most areas)) | /admin modulestestbot moderator -1001000001000 timezone America/Anchorage]
[Juneau (Alaska - Juneau area) | /admin modulestestbot moderator -1001000001000 timezone America/Juneau]
[Sitka (Alaska - Sitka area) | /admin modulestestbot moderator -1001000001000 timezone America/Sitka]
[Metlakatla (Alaska - Annette Island) | /admin modulestestbot moderator -1001000001000 timezone America/Metlakatla]
[Yakutat (Alaska - Yakutat) | /admin modulestestbot moderator -1001000001000 timezone America/Yakutat]
[Nome (Alaska (west)) | /admin modulestestbot moderator -1001000001000 timezone America/Nome]
[Adak (Aleutian Islands) | /admin modulestestbot moderator -1001000001000 timezone America/Adak]
[Prev | /admin modulestestbot moderator -1001000001000 timezone US 2] [Next | /admin modulestestbot moderator -1001000001000 timezone US 4]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone US 4') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › timezone: <b>Choose a primary city</b>

What time zone should be used in /events?

Choose a primary city:
[Honolulu (Hawaii) | /admin modulestestbot moderator -1001000001000 timezone Pacific/Honolulu]
[Prev | /admin modulestestbot moderator -1001000001000 timezone US 3] [\xa0 | /stop]
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 timezone America/Los_Angeles') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Set <code>timezone</code> to <code>America/Los_Angeles</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone (America/L…) • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""
