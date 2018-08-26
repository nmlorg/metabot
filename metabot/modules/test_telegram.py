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

    assert conversation.message('/admin modulestestbot telegram') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>',
            'reply_markup': {'inline_keyboard': [[{'text': 'Start bot', 'callback_data': '/admin modulestestbot telegram start'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot telegram start') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>\n'
                    '\n'
                    '@modulestestbot is now running.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Stop bot', 'callback_data': '/admin modulestestbot telegram stop'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot telegram start') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>\n'
                    '\n'
                    '@modulestestbot is already running.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Stop bot', 'callback_data': '/admin modulestestbot telegram stop'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot telegram stop') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>\n'
                    '\n'
                    '@modulestestbot is now offline.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Start bot', 'callback_data': '/admin modulestestbot telegram start'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot telegram stop') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a telegram: <b>Choose an action</b>\n'
                    '\n'
                    '@modulestestbot is not currently running.',
            'reply_markup': {'inline_keyboard': [[{'text': 'Start bot', 'callback_data': '/admin modulestestbot telegram start'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable
