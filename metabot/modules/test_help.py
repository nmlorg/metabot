"""Tests for metabot.modules.help."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import help  # pylint: disable=redefined-builtin


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(help)


# pylint: disable=line-too-long


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Verify the help module."""

    assert conversation.message('/nothelp') == ''

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
I don't have much documentation\u2014check with a bot admin!
"""

    assert conversation.message('/help') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/admin \u2013 Manage the admin list
"""

    assert conversation.message('/admin modulestestbot help hide admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a help: <b>Select a module</b>

<code>admin</code> is now hidden.
[Show admin (/admin \u2013 Manage the admin list) | /admin modulestestbot help unhide admin]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/help') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
I don't have much documentation\u2014check with a bot admin!
"""

    assert conversation.message('/admin modulestestbot help hide admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a help: <b>Select a module</b>

<code>admin</code> is already hidden!
[Show admin (/admin \u2013 Manage the admin list) | /admin modulestestbot help unhide admin]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot help unhide admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a help: <b>Select a module</b>

<code>admin</code> is now visible.
[Hide admin (/admin \u2013 Manage the admin list) | /admin modulestestbot help hide admin]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot help unhide admin') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a help: <b>Select a module</b>

<code>admin</code> is not hidden!
[Hide admin (/admin \u2013 Manage the admin list) | /admin modulestestbot help hide admin]
[Back | /admin modulestestbot]
"""
