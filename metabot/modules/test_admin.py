"""Tests for metabot.modules.admin."""

import pytest

from metabot.modules import admin


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(admin)


# pylint: disable=line-too-long


def test_invalid_user(conversation):  # pylint: disable=redefined-outer-name
    """Verify the bot doesn't respond to the /admin command from non-admins."""

    error_message = """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin

Hi! You aren't one of my admins. If you should be, ask a current admin to add you by opening a chat with me (@modulestestbot) and typing:

<pre>/admin modulestestbot admin add 2000</pre>
"""

    assert conversation.message('/admin', user_id=2000) == error_message
    assert conversation.message('/admin dummy', user_id=2000) == error_message
    assert conversation.message('/admin modulestestbot admin add 2000',
                                user_id=2000) == error_message


def test_default(conversation):  # pylint: disable=redefined-outer-name
    """Verify the /admin command gives its lovely menu of subcommands."""

    assert conversation.message('/notadmin') == ''

    assert conversation.message('/admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin: <b>Choose a bot</b>

This is a metabot! Check out https://github.com/nmlorg/metabot/issues to keep track of bugs and features.

To configure your bot, choose its username:
[modulestestbot | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot: <b>Choose a module</b>
[admin • Manage the admin list | /admin modulestestbot admin]
[help • Return the list of commands and other bot features | /admin modulestestbot help]
[Back | /admin]
"""


def test_whoami(conversation):  # pylint: disable=redefined-outer-name
    """Test /whoami."""

    assert conversation.message('/whoami') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<code>1000</code>
"""


def test_bootstrap(conversation):  # pylint: disable=redefined-outer-name
    """Test /_bootstrap."""

    assert conversation.bot.config['issue37'].pop('admin') == {'admins': [1000]}
    assert len(admin.BOOTSTRAP_TOKEN) == 32
    admin.BOOTSTRAP_TOKEN = 'bootstraptest'

    assert conversation.message('/_bootstrap') == ''
    assert conversation.bot.config['issue37'].get('admin') is None

    assert conversation.message('/_bootstrap bogus') == ''
    assert conversation.bot.config['issue37'].get('admin') is None

    assert conversation.message('/_bootstrap bootstraptest') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Added 1000 to the admin list.
"""
    assert conversation.bot.config['issue37'].get('admin') == {'admins': [1000]}

    assert conversation.message('/_bootstrap bootstraptest') == ''
    assert conversation.bot.config['issue37'].get('admin') == {'admins': [1000]}

    assert conversation.message('/_bootstrap bootstraptest', user_id=2000) == ''
    assert conversation.bot.config['issue37'].get('admin') == {'admins': [1000]}


def test_admins(conversation):  # pylint: disable=redefined-outer-name
    """Verify /admin's own configurator."""

    assert conversation.message('/admin modulestestbot admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('bogus value') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

I'm not sure what <code>bogus value</code> is—it's not a user id!

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('1000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

You can't remove yourself from the admin list.

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('2000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

Added 2000 to the admin list.

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Remove 2000 | /admin modulestestbot admin 2000]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/dummy', user_id=2000) == ''

    assert conversation.message('/admin modulestestbot admin bogus value') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

I'm not sure what <code>bogus value</code> is—it's not a user id!

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Remove User2000 (2000) | /admin modulestestbot admin 2000]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot admin 2000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

Removed 2000 from the admin list.

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('/whoami', forward_date=1000) == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

I can't tell exactly who sent that message, possibly because the sender enabled <a href="https://telegram.org/blog/unsend-privacy-emoji#anonymous-forwarding">Anonymous Forwarding</a>. You can either ask them to temporarily re-enable normal forwarding, or ask them to open a chat with me, type <code>/whoami</code>, then forward or copy/paste the number they receive to you (to copy/paste on to me).

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('/whoami', forward_date=1000, forward_from=2000) == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › admin: <b>Choose an admin</b>

Added 2000 to the admin list.

Forward a message from a user to add or remove them, or select an existing admin to remove.
[Remove User2000 (2000) | /admin modulestestbot admin 2000]
[Back | /admin modulestestbot]
"""
