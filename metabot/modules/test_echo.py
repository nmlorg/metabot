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

    assert conversation('/myecho') == []

    conversation.bot.get_modconf('echo')['myecho'] = 'These are the rules: Have fun!'

    assert conversation('/myecho') == [
        {
            'chat_id': 1000,
            'text': 'These are the rules: Have fun!',
        },
    ]  # yapf: disable


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME echo."""

    assert conversation('/admin modulestestbot echo') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>--don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation('echotest') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Type the message for /echotest</b>\n'
                    '\n'
                    'Type the text you want me to send in response to <code>/echotest</code>:',
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot echo'}]]},
        },
    ]  # yapf: disable

    assert conversation('my message') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    '/echotest now echoes <code>my message</code>.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>--don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': '/echotest (my message)', 'callback_data': '/admin modulestestbot echo echotest remove'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot echo echotest new message') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    'Changed /echotest from <code>my message</code> to <code>new message</code>.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>--don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': '/echotest (new message)', 'callback_data': '/admin modulestestbot echo echotest remove'}],
                                                 [{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot echo echotest remove') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    'Removed /echotest (<code>new message</code>).\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>--don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable

    assert conversation('/admin modulestestbot echo bogus remove') == [
        {
            'chat_id': 1000,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
            'text': 'Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>\n'
                    '\n'
                    '/bogus is not echoing anything.\n'
                    '\n'
                    "Type the name of a command to add (like <code>rules</code>--don't include a slash at the beginning!), or select an existing echo to remove.",
            'reply_markup': {'inline_keyboard': [[{'text': 'Back', 'callback_data': '/admin modulestestbot'}]]},
        },
    ]  # yapf: disable
