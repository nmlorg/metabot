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

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['myecho'] = (
        'These are the rules: Have fun!')

    assert conversation.message('/myecho') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
These are the rules: Have fun!
"""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['about'] = (
        'First line.\n'
        'Second line.\n'
        'Last line.')

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

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['rules1'] = (
        'These are the rules: Have fun!')
    conversation.multibot.conf['bots']['modulestestbot']['issue37']['echo']['rules2'] = (
        'These are the rules: Have fun!!')

    assert conversation.message(
        '/help', user_id=2000) == """\
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

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('EchoTest') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo \u203a echotest: <b>Type the message for /echotest</b>

Type the text you want me to send in response to <code>/echotest</code>:
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('my message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

/echotest now echoes <code>my message</code>.

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.
[/echotest (my message) | /admin modulestestbot echo echotest remove]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot echo echotest new message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

Changed /echotest from <code>my message</code> to <code>new message</code>.

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.
[/echotest (new message) | /admin modulestestbot echo echotest remove]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot echo echotest remove') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

Removed /echotest (<code>new message</code>).

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot echo bogus remove') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a echo: <b>Choose a command</b>

/bogus is not echoing anything.

Type the name of a command to add (like <code>rules</code>\u2014don't include a slash at the beginning!), or select an existing echo to remove.
[Back | /admin modulestestbot]
"""
