"""Tests for metabot.modules.echo."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import echo


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(echo)


# pylint: disable=line-too-long


def test_echo(conversation):  # pylint: disable=redefined-outer-name
    """Verify the echo module (which uses dynamic commands)."""

    assert conversation.message('/myecho') == []

    conversation.multibot.bots['modulestestbot']['echo']['myecho'] = (
        'These are the rules: Have fun!')

    assert conversation.message('/myecho') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'These are the rules: Have fun!',
        },
    ]  # yapf: disable

    conversation.multibot.bots['modulestestbot']['echo']['about'] = ('First line.\n'
                                                                     'Second line.\n'
                                                                     'Last line.')

    assert conversation.message('/about') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'First line.',
            'reply_markup': {'inline_keyboard': [[{'text': 'More (1/3)', 'callback_data': '/about 2'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/about 2') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'First line.\n'
                    '\n'
                    'Second line.',
            'reply_markup': {'inline_keyboard': [[{'text': 'More (2/3)', 'callback_data': '/about 3'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/about 3') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'First line.\n'
                    '\n'
                    'Second line.\n'
                    '\n'
                    'Last line.',
        },
    ]  # yapf: disable

    assert conversation.message('/about 1000') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'First line.\n'
                    '\n'
                    'Second line.\n'
                    '\n'
                    'Last line.',
        },
    ]  # yapf: disable

    assert conversation.message('/about bogus') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'First line.',
            'reply_markup': {'inline_keyboard': [[{'text': 'More (1/3)', 'callback_data': '/about 2'}]]},
        },
    ]  # yapf: disable


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    conversation.multibot.bots['modulestestbot']['echo']['rules1'] = (
        'These are the rules: Have fun!')
    conversation.multibot.bots['modulestestbot']['echo']['rules2'] = (
        'These are the rules: Have fun!!')

    assert conversation.message('/help', user_id=2000) == [
        {
            'chat_id': 2000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': '<b>Commands</b>\n'
                    '\n'
                    '/rules1 \u2013 &quot;These are the rules: Have fun!&quot;\n'
                    '\n'
                    '/rules2 \u2013 &quot;These are the rules: Have fun\u2026&quot;',
        },
    ]  # yapf: disable


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME echo."""

    assert conversation.message('/admin modulestestbot echo') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('EchoTest') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo \u203a echotest: <b>Type the message for /echotest</b>\n'
                    '\n'
                    'Type the text you want me to send in response to <code>/echotest</code>:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot echo'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('my message') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    '/echotest now echoes <code>my message</code>.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': '/echotest (my message)', 'callback_data': '/admin modulestestbot echo echotest remove'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot echo echotest new message') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    'Changed /echotest from <code>my message</code> to <code>new message</code>.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': '/echotest (new message)', 'callback_data': '/admin modulestestbot echo echotest remove'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot echo echotest remove') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    'Removed /echotest (<code>new message</code>).\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation.message('/admin modulestestbot echo bogus remove') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    '/bogus is not echoing anything.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable
