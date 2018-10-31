"""Self-managing bot/module configuration store."""

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import logging

from metabot.util import dicttools
from metabot.util import jsonutil


class BotConf(dicttools.ImplicitTrackingDict):
    """Self-managing bot/module configuration store."""

    def __init__(self, confdir=None):
        self.fname = confdir and confdir + '/multibot.json'
        data = self.fname and jsonutil.load(self.fname)
        super(BotConf, self).__init__(isinstance(data, dict) and data or {})

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
                    logging.info('[%s] %s: %r -> %r', ' '.join(userdata), '.'.join(path), orig,
                                 value)
                self.save()

    def save(self):
        """Serialize the store to disk (if confdir was provided at creation)."""

        if self.fname:
            jsonutil.dump(self.fname, self)
