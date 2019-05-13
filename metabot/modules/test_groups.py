"""Tests for metabot.modules.groups."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import groups


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(groups)


# pylint: disable=line-too-long


def test_conversation(conversation, requests_mock):  # pylint: disable=redefined-outer-name
    """Test /groups, @BOTNAME groups, and /admin BOTNAME groups."""

    assert conversation.message('/groups') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Group List

I don't know about any public groups yet, sorry!
"""

    assert conversation.message('/admin modulestestbot groups') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a groups: <b>Type a group username or invite link</b>

Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for the group you want to add, or select an existing group to remove:
[Back | /admin modulestestbot]
"""

    conversation.bot.get_chat.respond(
        json={
            'ok': True,
            'result': {
                'id': -1001000001000,
                'title': 'Dummy Public Group!',
                'username': 'DummyGroup',
                'type': 'supergroup',
                'description': 'Dummy public group'
            }
        })
    conversation.bot.get_chat_administrators.respond(
        json={
            'ok': True,
            'result': [{
                'user': {
                    'id': 1000,
                    'username': 'DummyUser'
                }
            }]
        })

    assert conversation.message('@dummygroup') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a groups: <b>Type a group username or invite link</b>

Added <b>Dummy Public Group!</b>.

Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for the group you want to add, or select an existing group to remove:
[Dummy Public Group! \u2022 DummyGroup | /admin modulestestbot groups remove 92aa63]
[Back | /admin modulestestbot]
"""

    requests_mock.get('https://t.me/joinchat/DUMMY_INVITE_LINK',
                      text="""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Telegram: Join Group Chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

<meta property="og:title" content="Dummy Private Group&#33;">
<meta property="og:image" content="https://cdn1.telesco.pe/file/DUMMY_PATH.jpg">
<meta property="og:site_name" content="Telegram">
<meta property="og:description" content="Dummy private group">
""")

    assert conversation.message('https://t.me/joinchat/DUMMY_INVITE_LINK') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a groups: <b>Type a group username or invite link</b>

Added <b>Dummy Private Group!</b>.

Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for the group you want to add, or select an existing group to remove:
[Dummy Private Group! \u2022 https://t.me/joinchat/DUMMY_INVITE_LINK | /admin modulestestbot groups remove c5bfc8]
[Dummy Public Group! \u2022 DummyGroup | /admin modulestestbot groups remove 92aa63]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/groups') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Group List: <b>Choose a location</b>
[Worldwide | /groups Worldwide]
"""

    assert conversation.message('/groups Worldwide') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Group List \u203a Worldwide

<a href="https://t.me/joinchat/DUMMY_INVITE_LINK">Dummy Private Group!</a>
Dummy private group

<a href="https://t.me/DummyGroup">Dummy Public Group!</a>
Dummy public group
[Back | /groups]
"""

    assert conversation.raw_inline('') == []

    assert conversation.raw_inline('groups') == [
        {
            'cache_time': 60,
            'inline_query_id': 2000,
            'results': [
                {
                    'description': 'Dummy private group',
                    'id': 'https://t.me/joinchat/DUMMY_INVITE_LINK',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<a href="https://t.me/joinchat/DUMMY_INVITE_LINK">Dummy Private Group!</a>\n'
                                        'Dummy private group',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Dummy Private Group! \u2022 https://t.me/joinchat/DUMMY_INVITE_LINK',
                    'type': 'article',
                },
                {
                    'description': 'Dummy public group',
                    'id': 'https://t.me/DummyGroup',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<a href="https://t.me/DummyGroup">Dummy Public Group!</a>\n'
                                        'Dummy public group',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Dummy Public Group! \u2022 DummyGroup',
                    'type': 'article',
                },
            ],
        }
    ]  # yapf: disable

    assert conversation.raw_inline('groups priva') == [
        {
            'cache_time': 60,
            'inline_query_id': 2000,
            'results': [
                {
                    'description': 'Dummy private group',
                    'id': 'https://t.me/joinchat/DUMMY_INVITE_LINK',
                    'input_message_content': {
                        'disable_web_page_preview': True,
                        'message_text': '<a href="https://t.me/joinchat/DUMMY_INVITE_LINK">Dummy Private Group!</a>\n'
                                        'Dummy private group',
                        'parse_mode': 'HTML',
                    },
                    'title': 'Dummy Private Group! \u2022 https://t.me/joinchat/DUMMY_INVITE_LINK',
                    'type': 'article',
                },
            ],
        }
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot groups remove blah') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a groups: <b>Type a group username or invite link</b>

Oops, the groups list changed since you loaded that screen, try again.

Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for the group you want to add, or select an existing group to remove:
[Dummy Private Group! \u2022 https://t.me/joinchat/DUMMY_INVITE_LINK | /admin modulestestbot groups remove c5bfc8]
[Dummy Public Group! \u2022 DummyGroup | /admin modulestestbot groups remove 92aa63]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot groups remove 92aa63') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a groups: <b>Type a group username or invite link</b>

Removed <b>Dummy Public Group!</b>.

Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for the group you want to add, or select an existing group to remove:
[Dummy Private Group! \u2022 https://t.me/joinchat/DUMMY_INVITE_LINK | /admin modulestestbot groups remove c5bfc8]
[Back | /admin modulestestbot]
"""


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/groups \u2013 Find other group chats
"""
