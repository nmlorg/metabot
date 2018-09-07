"""Tests for metabot.botconf."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

from metabot import botconf


def test_save_load(tmpdir):
    """Verify MultiBot can start with no config, can have a bot added, and can restart."""

    conffile = tmpdir.join('multibot.json')

    conf = botconf.BotConf(confdir=tmpdir.strpath)
    conf['alpha']['bravo'] = {'charlie': 'delta'}
    conf['alpha']['echo'] = [2, 4, 6]
    conf.save()

    assert json.loads(conffile.read()) == {
        'alpha': {
            'bravo': {
                'charlie': 'delta',
            },
            'echo': [2, 4, 6],
        },
    }
