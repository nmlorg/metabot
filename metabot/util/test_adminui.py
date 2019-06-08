"""Tests for metabot.util.adminui."""

import pytest

from metabot.modules import echo
from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(echo, moderator)


# pylint: disable=line-too-long


def test_bool(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.bool."""

    echoconf = conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['dummy']

    assert 'paginate' not in echoconf

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Enabled <code>paginate</code>.
[text \u2022 The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[paginate (yes) \u2022 For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) \u2022 Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[Back | /admin modulestestbot echo]
"""

    assert echoconf['paginate'] is True

    assert conversation.message('/admin modulestestbot echo dummy paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › dummy: <b>Choose a field</b>

Disabled <code>paginate</code>.
[text \u2022 The message, sticker, or image to send in response to /dummy. | /admin modulestestbot echo dummy text]
[paginate (no) \u2022 For multiline messages, display just one line at a time? | /admin modulestestbot echo dummy paginate]
[private (no) \u2022 Send the message in group chats, or just in private? | /admin modulestestbot echo dummy private]
[Back | /admin modulestestbot echo]
"""

    assert 'paginate' not in echoconf


def test_daysofweek(conversation):  # pylint: disable=redefined-outer-name
    """Test adminui.daysofweek."""

    groupconf = conversation.multibot.conf['bots']['modulestestbot']['issue37']['moderator'][
        '-1001000001000']
    groupconf['_dummy'] = 0

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

    assert 'dailydow' not in groupconf

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

    assert groupconf['dailydow'] == 127

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

    assert groupconf['dailydow'] == 125

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

    assert groupconf['dailydow'] == 61

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

    assert groupconf['dailydow'] == 53

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

    assert 'dailydow' not in groupconf
