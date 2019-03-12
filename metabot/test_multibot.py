"""Tests for metabot.multibot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import threading
import time

import ntelebot
import pytest
import yaml

from metabot import multibot


def test_add_bot():
    """Verify the basic behavior of add_bot."""

    mybot = multibot.MultiBot(())
    mockbot = ntelebot.bot.Bot('1234:badbot')
    mockbot.getme.respond(json={'description': 'Unauthorized', 'error_code': 401, 'ok': False})
    with pytest.raises(ntelebot.errors.Unauthorized):
        mybot.add_bot('1234:badbot')


def test_save_load(tmpdir):
    """Verify MultiBot can start with no config, can have a bot added, and can restart."""

    conffile = tmpdir.join('bots.yaml')

    mybot = multibot.MultiBot((), confdir=tmpdir.strpath)
    mockbot = ntelebot.bot.Bot('1234:goodbot')
    mockbot.getme.respond(json={'ok': True, 'result': {'id': 1234, 'username': 'goodbot'}})
    mockbot.getupdates.respond(json={'ok': True, 'result': []})
    mybot.add_bot('1234:goodbot')
    mybot.run_bot('goodbot')
    assert yaml.safe_load(conffile.read()) == {
        'goodbot': {
            'issue37': {
                'telegram': {
                    'running': True,
                    'token': '1234:goodbot',
                },
            },
        },
    }

    tmpdir.join('calendars.json').write(
        json.dumps([
            {
                'calid': 'static:test_multibot',
                'name': 'MultiBot Test Calendar',
            },
        ]))

    newbot = multibot.MultiBot((), confdir=tmpdir.strpath)
    assert newbot.conf == mybot.conf
    assert newbot.calendars == {
        'c9328778': {
            'calid': 'static:test_multibot',
            'name': 'MultiBot Test Calendar',
        },
    }

    mybot.stop_bot('goodbot')
    newbot.stop_bot('goodbot')


def test_module():
    """Verify the configurable module dispatcher."""

    results = []

    def dummymod(ctx):  # pylint: disable=missing-docstring
        _ = ctx
        results.append(ctx.text)
        time.sleep(.5)

    mybot = multibot.MultiBot({dummymod})
    mockbot = ntelebot.bot.Bot('1234:modbot')
    mockbot.getme.respond(json={'ok': True, 'result': {'id': 1234, 'username': 'modbot'}})
    user = {'id': 1000}
    chat = {'id': 1000, 'type': 'private'}
    message = {'message_id': 2000, 'chat': chat, 'from': user, 'text': '/dummymod test'}
    update = {'message': message, 'update_id': 3000}
    mockbot.getupdates.respond(json={'ok': True, 'result': [update]})
    mybot.add_bot('1234:modbot')
    mybot.run_bot('modbot')
    threading.Timer(.1, mybot.stop).start()
    mybot.run()
    assert results == ['test']
