"""Tests for metabot.botconf."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import yaml

from metabot import botconf


# See https://github.com/yaml/pyyaml/issues/202.
@pytest.mark.filterwarnings('ignore:Using or importing the ABCs from')
def test_save_load(tmpdir):
    """Verify MultiBot can start with no config, can have a bot added, and can restart."""

    conffile = tmpdir.join('autogen.yaml')

    conf = botconf.BotConf(confdir=tmpdir.strpath)
    conf['autogen']['alpha']['bravo'] = {'charlie': 'delta'}
    conf['autogen']['alpha']['echo'] = [2, 4, 6]
    conf.save()

    assert yaml.safe_load(conffile.read()) == {
        'alpha': {
            'bravo': {
                'charlie': 'delta',
            },
            'echo': [2, 4, 6],
        },
    }
