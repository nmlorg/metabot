"""Tests for metabot.modules.countdown."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

import pytest

from metabot.modules import countdown


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(countdown)


def test_countdown(conversation):  # pylint: disable=redefined-outer-name
    """Verify the countdown module (which uses dynamic commands)."""

    assert conversation('/mycountdown') == []

    conversation.bot.get_modconf('countdown')['mycountdown'] = 1534906800

    ret = conversation('/mycountdown')
    assert len(ret) == 1
    assert ret[0]['text'].endswith(' ago')


def test_format_delta():
    """Verify the time delta formatter."""

    when = datetime.datetime(2018, 8, 21, 20)
    assert countdown.format_delta(when - datetime.datetime(2018, 8, 21, 20)) == '<b>NOW</b>'
    assert (countdown.format_delta(when - datetime.datetime(2018, 8, 21, 19, 59, 59, 500000)) ==
            '<b>0.5</b> seconds')
    assert (countdown.format_delta(when - datetime.datetime(2018, 8, 21, 19, 59, 58, 500000)) ==
            '<b>1.5</b> seconds')
    assert (countdown.format_delta(when - datetime.datetime(2018, 8, 21, 19, 58, 59)) ==
            '<b>1</b> minute, <b>1.0</b> second')
    assert (countdown.format_delta(when - datetime.datetime(2017, 8, 21, 18, 58)) ==
            '<b>365</b> days, <b>1</b> hour, <b>2</b> minutes')
