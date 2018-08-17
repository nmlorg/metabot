"""Tests for metabot.multibot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import time

import ntelebot

from metabot import multibot


def test_save_load(tmpdir):
    """Verify MultiBot can start with no config, can have a bot added, and can restart."""

    conffile = tmpdir.join('multibot.json')

    mybot = multibot.MultiBot({'dummymod': lambda ctx: 'DUMMYMOD'}, fname=conffile.strpath)
    mockbot = ntelebot.bot.Bot('1234:goodbot')
    mockbot.getme.respond(json={'ok': True, 'result': {'id': 1234, 'username': 'goodbot'}})
    mockbot.getupdates.respond(json=lambda request, context: time.sleep(1))
    mybot.add_bot({'token': '1234:goodbot', 'modules': {'dummymod': {}}})
    mybot.save()
    assert json.loads(conffile.read()) == mybot.bots

    newbot = multibot.MultiBot({'dummymod': lambda ctx: 'DUMMYMOD'}, fname=conffile.strpath)
    assert newbot.bots == mybot.bots
