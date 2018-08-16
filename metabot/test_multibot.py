"""Tests for metabot.multibot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

from metabot import multibot


class MockBot(object):
    # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, token):
        self.token = token

    def get_me(self):
        bot_id, username = self.token.split(':', 1)
        return {'id': int(bot_id), 'username': username}


def test_save_load(monkeypatch, tmpdir):
    """Verify MultiBot can start with no config, can have a bot added, and can restart."""

    conffile = tmpdir.join('multibot.json')

    class MockMultiBot(multibot.MultiBot):  # pylint: disable=missing-docstring
        fname = conffile.strpath

    monkeypatch.setattr('ntelebot.bot.Bot', MockBot)

    mybot = MockMultiBot({
        'dummymod': lambda ctx: 'DUMMYMOD',
    })
    mybot.add_bot({'token': '1234:goodbot', 'modules': {'dummymod': {}}})
    mybot.save()
    assert json.loads(conffile.read()) == mybot.bots

    newbot = MockMultiBot({
        'dummymod': lambda ctx: 'DUMMYMOD',
    })
    assert newbot.bots == mybot.bots
