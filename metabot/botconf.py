"""Self-managing bot/module configuration store."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from metabot import util


class BotConf(util.dicttools.ImplicitTrackingDict):
    """Self-managing bot/module configuration store."""

    def __init__(self, fname=None):
        self.fname = fname
        data = fname and util.json.load(fname)
        super(BotConf, self).__init__(isinstance(data, dict) and data or {})

    def save(self):
        """Serialize the store to disk (if fname was provided at creation)."""

        if self.fname:
            util.json.dump(self.fname, self)

    def __enter__(self):
        pass

    def __exit__(self, unused_exc_type, unused_exc_value, unused_traceback):
        log = self.finalize()
        if log:
            for path, (value, orig) in sorted(log.items()):
                logging.info('%s: %r -> %r', '.'.join(path), orig, value)
            self.save()
