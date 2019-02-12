"""Tests for metabot.modules.telegram."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import telegram


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(telegram)


# pylint: disable=line-too-long


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME telegram."""

    assert conversation.message('/admin modulestestbot telegram') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>
[Start bot | /admin modulestestbot telegram start]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot telegram start') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>

@modulestestbot is now running.
[Stop bot | /admin modulestestbot telegram stop]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot telegram start') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>

@modulestestbot is already running.
[Stop bot | /admin modulestestbot telegram stop]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot telegram stop') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>

@modulestestbot is now offline.
[Start bot | /admin modulestestbot telegram start]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot telegram stop') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>

@modulestestbot is not currently running.
[Start bot | /admin modulestestbot telegram start]
[Back | /admin modulestestbot]
"""
