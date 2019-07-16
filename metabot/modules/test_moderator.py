"""Tests for metabot.modules.moderator."""

import pytest

from metabot.modules import moderator


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(moderator)


# pylint: disable=line-too-long


def test_forward(conversation):  # pylint: disable=redefined-outer-name
    """Test autoforward."""

    assert conversation.message('Test Forward', chat_type='channel') == ''

    conversation.bot.config['issue37']['moderator']['-1002000002000']['forward'][
        'from'] = -1001000001000

    assert conversation.message('Test Forward', chat_type='channel') == """\
[chat_id=-1002000002000 disable_notification=True from_chat_id=-1001000001000 message_id=2000]
(EMPTY MESSAGE)
"""


def test_mod(conversation):  # pylint: disable=redefined-outer-name
    """Test /mod."""

    modconf = conversation.bot.config['issue37']['moderator']
    groupdata = conversation.multibot.conf['groups']
    modconf['-1001000001000']['title'] = groupdata[-1001000001000]['title'] = 'Mod Test'
    modconf['-1002000002000']['title'] = groupdata[-1002000002000]['title'] = 'Hidden Group'

    assert conversation.message('/mod', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
Group Admin: <b>Become a group admin</b>

Hi! You aren't an admin in any groups I'm in. If you should be, ask a current admin to promote you from the group's members list.
"""

    conversation.multibot.conf['groups'][-1001000001000]['admins'] = [2000]

    assert conversation.message('/mod', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
Group Admin: <b>Choose a group</b>
[-1001000001000 • Mod Test | /mod -1001000001000]
"""

    assert conversation.message('/mod -1002000002000', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
Group Admin: <b>Choose a group</b>

I can't set <code>-1002000002000</code>.
[-1001000001000 • Mod Test | /mod -1001000001000]
"""

    assert conversation.message('/mod -1001000001000', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
Group Admin › -1001000001000: <b>Choose a field</b>
[calendars • Which calendars should be listed in /events? | /mod -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /mod -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /mod -1001000001000 forward]
[greeting • How should I greet people when they join? | /mod -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /mod -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /mod -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /mod -1001000001000 timezone]
[Back | /mod]
"""


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME moderator."""

    assert conversation.message('/admin modulestestbot moderator') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator: <b>Add me to a group</b>

I'm not in any groups! Add me to an existing group from its details screen.
[Back | /admin modulestestbot]
"""

    adding_user = {'id': 2000}
    joined_user = {'id': 3000, 'is_bot': True, 'first_name': 'User 3000'}
    chat = {'id': -1001000001000, 'type': 'supergroup', 'title': 'My Group'}
    message = {
        'from': adding_user,
        'chat': chat,
        'message_id': 5000,
        'new_chat_members': [joined_user],
    }
    join_update = {'message': message}
    # Let the bot notice it's in the test group.
    conversation.multibot.dispatcher(conversation.bot, join_update)

    assert conversation.message('/admin modulestestbot moderator') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator: <b>Choose a group</b>
[-1001000001000 • My Group | /admin modulestestbot moderator -1001000001000]
[Back | /admin modulestestbot]
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

    assert conversation.message('/admin modulestestbot moderator -1001000001000 bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

I can't set <code>bogus</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › greeting: <b>Type a new value for greeting</b>

How should I greet people when they join?

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message(
        'Welcome to chat title, new users! <b>Initial</b> pinned message.') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Set <code>greeting</code> to <code>Welcome to chat title, new users! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting (Welcome t…) • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    replies = conversation.raw_message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == []

    joined_user['is_bot'] = False

    replies = conversation.raw_message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == [
        {
            'chat_id': -1001000001000,
            'disable_notification': True,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome to My Group, <a href="tg://user?id=3000">User 3000</a>! <b>Initial</b> pinned message.',
        },
    ]  # yapf: disable

    message = {
        'from': adding_user,
        'chat': chat,
        'message_id': 5000,
        'pinned_message': {
            'message_id': 6000,
        },
    }
    pin_update = {'message': message}
    conversation.multibot.dispatcher(conversation.bot, pin_update)

    replies = conversation.raw_message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == [
        {
            'chat_id': -1001000001000,
            'disable_notification': True,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome to My Group, <a href="tg://user?id=3000">User 3000</a>! <b>Initial</b> <a href="https://t.me/c/1000001000/6000">pinned message</a>.',
        },
    ]  # yapf: disable

    # This group is now public!
    chat['username'] = 'mygroup'

    replies = conversation.raw_message('/dummy')
    assert replies == []
    conversation.multibot.dispatcher(conversation.bot, join_update)
    assert replies == [
        {
            'chat_id': -1001000001000,
            'disable_notification': True,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'reply_to_message_id': 5000,
            'text': 'Welcome to My Group, <a href="tg://user?id=3000">User 3000</a>! <b>Initial</b> <a href="https://t.me/mygroup/6000">pinned message</a>.',
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › greeting: <b>Type a new value for greeting</b>

How should I greet people when they join?

<code>greeting</code> is currently <code>Welcome to chat title, new users! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code>.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('Welcome! New message.') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Changed <code>greeting</code> from <code>Welcome to chat title, new users! &lt;b&gt;Initial&lt;/b&gt; pinned message.</code> to <code>Welcome! New message.</code>.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting (Welcome! …) • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message('/admin modulestestbot moderator -1001000001000 greeting') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000 › greeting: <b>Type a new value for greeting</b>

How should I greet people when they join?

<code>greeting</code> is currently <code>Welcome! New message.</code>.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot moderator -1001000001000]
"""

    assert conversation.message('OFF') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

Unset <code>greeting</code> (was <code>Welcome! New message.</code>).
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""

    assert conversation.message(
        '/admin modulestestbot moderator -1001000001000 greeting OFF') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › moderator › -1001000001000: <b>Choose a field</b>

<code>greeting</code> is already unset.
[calendars • Which calendars should be listed in /events? | /admin modulestestbot moderator -1001000001000 calendars]
[daily • Should I announce upcoming events once a day? | /admin modulestestbot moderator -1001000001000 daily]
[forward • Automatically forward messages from one chat to this one. | /admin modulestestbot moderator -1001000001000 forward]
[greeting • How should I greet people when they join? | /admin modulestestbot moderator -1001000001000 greeting]
[maxeventscount • How many events should be listed in /events? | /admin modulestestbot moderator -1001000001000 maxeventscount]
[maxeventsdays • How many days into the future should /events look? | /admin modulestestbot moderator -1001000001000 maxeventsdays]
[timezone • What time zone should be used in /events? | /admin modulestestbot moderator -1001000001000 timezone]
[Back | /admin modulestestbot moderator]
"""
