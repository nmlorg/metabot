"""Tests for metabot.modules.help."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import help  # pylint: disable=redefined-builtin


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(help)


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Verify the help module."""

    assert conversation.message('/nothelp') == []
    assert conversation.message('/help') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Commands</b>\n'
                    '\n'
                    "/admin \u2013 Manage the bot's state and settings",
            'reply_markup': {'inline_keyboard': []},
        },
    ]  # yapf: disable

    assert conversation.message('/help', user_id=2000) == [
        {
            'chat_id': 2000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': "I don't have much documentation\u2014check with a bot admin!",
            'reply_markup': {'inline_keyboard': []},
        },
    ]  # yapf: disable
