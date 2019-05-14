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

    assert conversation.message('/myecho') == ''

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['myecho'] = {
        'text': 'These are the rules: Have fun!',
    }

    assert conversation.message('/myecho') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
These are the rules: Have fun!
"""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['about'] = {
        'text': ('First line.\n'
                 'Second line.\n'
                 ' \n'
                 'Last line.'),
    }

    assert conversation.message('/about') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.
Second line.
 
Last line.
"""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['about'] = {
        'text': ('First line.\n'
                 'Second line.\n'
                 ' \n'
                 'Last line.'),
        'paginate': True,
    }

    assert conversation.message('/about') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.
[More (1/3) | /about 2]
"""

    assert conversation.message('/about 2') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.

Second line.
[More (2/3) | /about 3]
"""

    assert conversation.message('/about 3') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.

Second line.

Last line.
"""

    assert conversation.message('/about 1000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.

Second line.

Last line.
"""

    assert conversation.message('/about bogus') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
First line.
[More (1/3) | /about 2]
"""


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['rules1'] = {
        'text': 'These are the rules: Have fun!',
    }
    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['rules2'] = {
        'text': 'These are the rules: Have fun!!',
    }

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/rules1 \u2013 &quot;These are the rules: Have fun!&quot;

/rules2 \u2013 &quot;These are the rules: Have fun\u2026&quot;
"""


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME echo."""

    assert conversation.message('/admin modulestestbot echo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo.
[Back | /admin modulestestbot]
"""

    assert conversation.message('EchoTest') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo \u203a echotest: <b>Choose a field</b>
[text \u2022 The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[paginate \u2022 For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private \u2022 Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('text') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo \u203a echotest \u203a text: <b>Type a new value for text</b>

The message, sticker, or image to send in response to /echotest.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot echo echotest]
"""

    assert conversation.message('my message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo \u203a echotest: <b>Choose a field</b>

Set <code>text</code> to <code>my message</code>.
[text \u2022 The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[paginate \u2022 For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private \u2022 Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('/admin modulestestbot echo echotest text new message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo \u203a echotest: <b>Choose a field</b>

Changed <code>text</code> from <code>my message</code> to <code>new message</code>.
[text \u2022 The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[paginate \u2022 For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private \u2022 Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('/admin modulestestbot echo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo.
[/echotest (new message) | /admin modulestestbot echo echotest]
[Back | /admin modulestestbot]
"""
