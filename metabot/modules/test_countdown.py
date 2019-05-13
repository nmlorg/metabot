"""Tests for metabot.modules.countdown."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import countdown


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(countdown)


# pylint: disable=line-too-long


def test_countdown(conversation):  # pylint: disable=redefined-outer-name
    """Verify the countdown module (which uses dynamic commands)."""

    assert conversation.message('/mycountdown') == ''

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['countdown'][
        'mycountdown'] = 1534906800
    assert conversation.message('/mycountdown').endswith(' ago\n')

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['countdown'][
        'mycountdown'] = 15349068000
    assert not conversation.message('/mycountdown').endswith(' ago\n')


def test_format_delta():
    """Verify the time delta formatter."""

    assert countdown.format_delta(0.) == '<b>NOW</b>'
    assert countdown.format_delta(1 / 9) == '<b>0.11</b> seconds'
    assert countdown.format_delta(1.5) == '<b>1.5</b> seconds'
    assert countdown.format_delta(61.) == '<b>1</b> minute, <b>1</b> second'
    assert countdown.format_delta(
        ((365 * 24 + 1) * 60 + 2) * 60.) == '<b>365</b> days, <b>1</b> hour, <b>2</b> minutes'


def test_help(conversation):  # pylint: disable=redefined-outer-name
    """Test /help."""

    conversation.multibot.conf['bots']['modulestestbot']['issue37']['countdown'][
        'count1'] = 1534906800
    conversation.multibot.conf['bots']['modulestestbot']['issue37']['countdown'][
        'count2'] = 15349068000

    assert conversation.message('/help', user_id=2000) == """\
[chat_id=2000 disable_web_page_preview=True parse_mode=HTML]
<b>Commands</b>

/count1 \u2013 Count up from 1534906800

/count2 \u2013 Count down to 15349068000
"""


def test_admin(conversation):  # pylint: disable=redefined-outer-name
    """Test /admin BOTNAME countdown."""

    assert conversation.message('/admin modulestestbot countdown') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown: <b>Choose a command</b>

Type the name of a command to add (like <code>days</code>\u2014don't include a slash at the beginning!), or select an existing countdown to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('CountDownTest') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown \u203a countdowntest: <b>Type the time for /countdowntest</b>

This is a little technical (it will be made simpler in the future), but type the unix timestamp to count down to.

(Go to https://www.epochconverter.com/, fill out the section "Human date to Timestamp", then use the number listed next to "Epoch timestamp".)
[Back | /admin modulestestbot countdown]
"""

    assert conversation.message('1534906800') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown: <b>Choose a command</b>

/countdowntest is now counting down to <code>1534906800</code>.

Type the name of a command to add (like <code>days</code>\u2014don't include a slash at the beginning!), or select an existing countdown to remove.
[/countdowntest (1534906800) | /admin modulestestbot countdown countdowntest remove]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot countdown countdowntest 1000') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown: <b>Choose a command</b>

Changed /countdowntest from <code>1534906800</code> to <code>1000</code>.

Type the name of a command to add (like <code>days</code>\u2014don't include a slash at the beginning!), or select an existing countdown to remove.
[/countdowntest (1000) | /admin modulestestbot countdown countdowntest remove]
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot countdown countdowntest bogus<>') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown \u203a countdowntest: <b>Type the time for /countdowntest</b>

I'm not sure how to count down to <code>bogus&lt;&gt;</code>!

This is a little technical (it will be made simpler in the future), but type the unix timestamp to count down to.

(Go to https://www.epochconverter.com/, fill out the section "Human date to Timestamp", then use the number listed next to "Epoch timestamp".)
[Back | /admin modulestestbot countdown]
"""

    assert conversation.message('remove') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown: <b>Choose a command</b>

Removed /countdowntest (which was counting down to <code>1000</code>).

Type the name of a command to add (like <code>days</code>\u2014don't include a slash at the beginning!), or select an existing countdown to remove.
[Back | /admin modulestestbot]
"""

    assert conversation.message('/admin modulestestbot countdown bogus remove') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
Bot Admin \u203a modulestestbot \u203a countdown: <b>Choose a command</b>

/bogus is not currently counting down to anything.

Type the name of a command to add (like <code>days</code>\u2014don't include a slash at the beginning!), or select an existing countdown to remove.
[Back | /admin modulestestbot]
"""
