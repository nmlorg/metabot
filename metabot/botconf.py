"""Self-managing bot/module configuration store."""

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import logging
import os

from metabot.util import dicttools
from metabot.util import jsonutil
from metabot.util import yamlutil


class BotConf(dicttools.ImplicitTrackingDict):
    """Self-managing bot/module configuration store."""

    confdir = None

    def __init__(self, confdir=None):  # pylint: disable=too-many-branches
        super(BotConf, self).__init__()
        if confdir:
            self.confdir = confdir
            if not os.path.isdir(confdir):
                os.makedirs(confdir, 0o700)
            else:
                for fname in os.listdir(confdir):
                    if fname.endswith('.yaml'):
                        self[fname[:-len('.yaml')]] = yamlutil.load(os.path.join(confdir, fname))

            # Schema update: Remove after 2019-03-26 (https://github.com/nmlorg/metabot/issues/18).
            if not self['bots']:
                fname = os.path.join(confdir, 'multibot.json')
                data = jsonutil.load(fname)
                if data:
                    self['bots'] = data
                    logging.info('Converted %s to %s.', fname, os.path.join(confdir, 'bots.yaml'))

            # Schema update: Remove after 2019-04-05 (https://github.com/nmlorg/metabot/issues/18).
            for botconf in self['bots'].values():
                for groupid, groupconf in botconf['moderator'].items():
                    groupid = int(groupid)
                    for k in ('title', 'type', 'username'):
                        if k in groupconf:
                            self['groups'][groupid][k] = groupconf[k]

            # Schema update: Remove after 2019-06-12 (https://github.com/nmlorg/metabot/issues/37).
            for botconf in self['bots'].values():
                if botconf.get('telegram'):
                    for modname in list(botconf):
                        if modname != 'issue37':
                            botconf['issue37'][modname] = botconf[modname]
                            botconf.pop(modname)

            # Schema update: Remove after 2019-08-13 (https://github.com/nmlorg/metabot/issues/41).
            for botconf in self['bots'].values():
                for command, message in botconf['issue37']['echo'].items():
                    if not isinstance(message, dict):
                        botconf['issue37']['echo'][command] = {
                            'text': message,
                            'paginate': True,
                            'private': '\n' in message,
                        }

        self._fnames = set(self)

    @contextlib.contextmanager
    def record_mutations(self, ctx):
        """Capture and record all changes to the bot config."""

        try:
            yield self
        finally:
            log = self.finalize()
            if log:
                userdata = ['%s' % ctx.user['id']]
                if ctx.user.get('username'):
                    userdata.append('@' + ctx.user['username'])
                if ctx.user.get('first_name') or ctx.user.get('last_name'):
                    userdata.append(
                        repr('%s %s' % (ctx.user.get('first_name', ''), ctx.user.get(
                            'last_name', ''))).strip())
                for path, (value, orig) in sorted(log.items()):
                    pathstr = '.'.join('%s' % part for part in path)
                    logging.info('[%s] %s: %r -> %r', ' '.join(userdata), pathstr, orig, value)
                self.save()

    def save(self):
        """Serialize the store to disk (if confdir was provided at creation)."""

        if self.confdir:
            for fname in self._fnames.difference(self):
                os.remove(os.path.join(self.confdir, fname + '.yaml'))
            self._fnames = set(self)
            for fname, data in self.items():
                yamlutil.dump(os.path.join(self.confdir, fname + '.yaml'), data)
