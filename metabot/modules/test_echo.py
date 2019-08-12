"""Tests for metabot.modules.echo."""

import pytest

from metabot.modules import echo


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(echo)


# pylint: disable=line-too-long


def test_echo(conversation):  # pylint: disable=redefined-outer-name
    """Verify the echo module (which uses dynamic commands)."""

    assert conversation.message('/myecho') == ''

    conversation.bot.config['issue37']['echo']['myecho'] = {
        'text': 'These are the rules: Have fun!',
    }

    assert conversation.message('/myecho') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
These are the rules: Have fun!
"""

    conversation.bot.config['issue37']['echo']['about'] = {
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

    conversation.bot.config['issue37']['echo']['about'] = {
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

    conversation.bot.config['issue37']['echo']['rules1'] = {
        'text': 'These are the rules: Have fun!',
    }
    conversation.bot.config['issue37']['echo']['rules2'] = {
        'text': 'These are the rules: Have fun!!',
    }

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/rules1 – &quot;These are the rules: Have fun!&quot;

/rules2 – &quot;These are the rules: Have fun…&quot;
"""


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME echo."""

    assert conversation.message('/admin modulestestbot echo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo: <b>Choose a command</b>

Type the name of a command to add (like <code>rules</code>—don't include a slash at the beginning!), or select an existing echo.
[Back | /admin modulestestbot]
"""

    assert conversation.message('EchoTest') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › echotest: <b>Choose a field</b>
[paginate (no) • For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[text • The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('text') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › echotest › text: <b>Type a new value for text</b>

The message, sticker, or image to send in response to /echotest.

Type your new value, or type "off" to disable/reset to default.
[Back | /admin modulestestbot echo echotest]
"""

    assert conversation.message('my message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › echotest: <b>Choose a field</b>

Set <code>text</code> to <code>my message</code>.
[paginate (no) • For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[text (my message) • The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('/admin modulestestbot echo echotest text new message') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › echotest: <b>Choose a field</b>

Changed <code>text</code> from <code>my message</code> to <code>new message</code>.
[paginate (no) • For multiline messages, display just one line at a time? | /admin modulestestbot echo echotest paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo echotest private]
[text (new messa…) • The message, sticker, or image to send in response to /echotest. | /admin modulestestbot echo echotest text]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('/admin modulestestbot echo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo: <b>Choose a command</b>

Type the name of a command to add (like <code>rules</code>—don't include a slash at the beginning!), or select an existing echo.
[echotest • new message | /admin modulestestbot echo echotest]
[Back | /admin modulestestbot]
"""

    assert conversation.message('textless paginate') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo › textless: <b>Choose a field</b>

Enabled <code>paginate</code>.
[paginate (yes) • For multiline messages, display just one line at a time? | /admin modulestestbot echo textless paginate]
[private (no) • Send the message in group chats, or just in private? | /admin modulestestbot echo textless private]
[text • The message, sticker, or image to send in response to /textless. | /admin modulestestbot echo textless text]
[Back | /admin modulestestbot echo]
"""

    assert conversation.message('/admin modulestestbot echo') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin › modulestestbot › echo: <b>Choose a command</b>

Type the name of a command to add (like <code>rules</code>—don't include a slash at the beginning!), or select an existing echo.
[echotest • new message | /admin modulestestbot echo echotest]
[textless | /admin modulestestbot echo textless]
[Back | /admin modulestestbot]
"""
