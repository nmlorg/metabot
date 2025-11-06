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

    bot = mybot.mgr.bot(1111111111).bot_api
    assert isinstance(bot, ntelebot.bot.Bot)
    assert mybot.mgr._bot_instances == {1111111111: bot}  # pylint: disable=protected-access
    assert mybot.mgr.bot(1111111111).bot_username == 'managertestbot'

    with pytest.raises(KeyError):
        mybot.mgr.bot('unknownbot')

    with pytest.raises(KeyError):
        mybot.mgr.bot(2222222222)


def test_cross_context():  # pylint: disable=too-many-statements
    """Test things that access multiple contexts."""

    mybot = multibot.MultiBot(())
    assert mybot.conf == {
        'bots': {},
    }
    mybot.conf['bots']['managertestbot']['issue37']['telegram']['token'] = '1111111111:BBBBBBBBBB'

    mgr = mybot.mgr
    with pytest.raises(AttributeError):
        assert mgr.bot_id == 1111111111
    with pytest.raises(AttributeError):
        assert mgr.chat_id == 90000000000
    with pytest.raises(AttributeError):
        assert mgr.chat_conf == {}
    with pytest.raises(AttributeError):
        assert mgr.user_id == 1000
    with pytest.raises(AttributeError):
        assert mgr.user_conf == {}
    with pytest.raises(AttributeError):
        assert not mgr.is_chat_admin

    mgr = mgr.bot(1111111111)
    assert mgr.bot_id == 1111111111
    with pytest.raises(AttributeError):
        assert mgr.chat_id == 90000000000
    with pytest.raises(AttributeError):
        assert mgr.chat_conf == {}
    with pytest.raises(AttributeError):
        assert mgr.user_id == 1000
    with pytest.raises(AttributeError):
        assert mgr.user_conf == {}
    with pytest.raises(AttributeError):
        assert not mgr.is_chat_admin
    assert mybot.conf == {
        'bots': {
            'managertestbot': {
                'issue37': {
                    'events': {
                        'users': {},
                    },
                    'moderator': {},
                    'telegram': {
                        'token': '1111111111:BBBBBBBBBB',
                    },
                },
            },
        },
    }

    mgr = mgr.user(1000)
    assert mgr.bot_id == 1111111111
    with pytest.raises(AttributeError):
        assert mgr.chat_id == 90000000000
    with pytest.raises(AttributeError):
        assert mgr.chat_conf == {}
    assert mgr.user_id == 1000
    assert mgr.user_conf == {}
    with pytest.raises(AttributeError):
        assert not mgr.is_chat_admin
    assert mybot.conf == {
        'bots': {
            'managertestbot': {
                'issue37': {
                    'events': {
                        'users': {
                            '1000': {},
                        },
                    },
                    'moderator': {},
                    'telegram': {
                        'token': '1111111111:BBBBBBBBBB',
                    },
                },
            },
        },
        'groups': {},
    }

    mgr = mgr.chat(90000000000)
    assert mgr.bot_id == 1111111111
    assert mgr.chat_id == 90000000000
    assert mgr.chat_conf == {}
    assert mgr.user_id == 1000
    assert mgr.user_conf == {}
    assert not mgr.is_chat_admin
    assert mybot.conf == {
        'bots': {
            'managertestbot': {
                'issue37': {
                    'events': {
                        'users': {
                            '1000': {},
                        },
                    },
                    'moderator': {
                        '90000000000': {},
                    },
                    'telegram': {
                        'token': '1111111111:BBBBBBBBBB',
                    },
                },
            },
        },
        'groups': {
            90000000000: {},
        },
    }

    mybot.conf['groups'][90000000000]['admins'] = [1000]
    assert mgr.is_chat_admin
