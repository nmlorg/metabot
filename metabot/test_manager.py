"""Tests for metabot.manager."""

import ntelebot
import pytest

from metabot import multibot


def test_simple():
    """Basic functionality."""

    mybot = multibot.MultiBot(())
    assert mybot.conf == {
        'bots': {},
    }
    assert mybot.mgr._bot_instances == {}  # pylint: disable=protected-access

    ntelebot.bot.Bot('1111111111:AAAAAAAAAA').getme.respond(json={
        'ok': True,
        'result': {
            'username': 'managertestbot',
        }
    })

    assert mybot.add_bot('1111111111:AAAAAAAAAA') == 'managertestbot'
    assert mybot.conf == {
        'bots': {
            'managertestbot': {
                'issue37': {
                    'telegram': {
                        'running': False,
                        'token': '1111111111:AAAAAAAAAA',
                    },
                },
            },
        },
    }
    assert mybot.mgr._bot_instances == {}  # pylint: disable=protected-access

    assert mybot.mgr.bot('managertestbot').bot_id == 1111111111
    assert mybot.mgr.bot(1111111111).bot_username == 'managertestbot'
    assert mybot.mgr.bot('1111111111').bot_username == 'managertestbot'
    assert mybot.mgr._bot_instances == {}  # pylint: disable=protected-access

    bot = mybot.mgr.bot(1111111111).bot_instance
    assert isinstance(bot, ntelebot.bot.Bot)
    assert mybot.mgr._bot_instances == {1111111111: bot}  # pylint: disable=protected-access
    assert mybot.mgr.bot(1111111111).bot_username == 'managertestbot'

    with pytest.raises(KeyError):
        mybot.mgr.bot('unknownbot')

    with pytest.raises(KeyError):
        mybot.mgr.bot(2222222222)
