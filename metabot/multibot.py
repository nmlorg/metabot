"""An ntelebot.loop.Loop that manages multiple bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import ntelebot

from metabot import util


class MultiBot(object):
    """An ntelebot.loop.Loop that manages multiple bots."""

    def __init__(self, modules, fname=None):
        self.modules = []
        self.dispatcher = ntelebot.dispatch.LoopDispatcher()
        for module in modules:
            modname = module.__name__.rsplit('.', 1)[-1]
            self.modules.append(modname)
            self.dispatcher.add(module)
        self.modules.sort()
        self.fname = fname
        self.loop = ntelebot.loop.Loop()

        bots = fname and util.json.load(fname)
        if bots and isinstance(bots, dict):
            self.bots = bots
        else:
            self.bots = {}

        for username, bot_config in self.bots.items():
            if bot_config['running']:
                self.run_bot(username)

    def add_bot(self, token):
        """Begin polling bot_config.token, dispatching updates through bot_config.modules."""

        bot_info = ntelebot.bot.Bot(token).get_me()
        self.bots[bot_info['username']] = {
            'modules': {},
            'running': False,
            'token': token,
        }
        self.save()
        return bot_info['username']

    def _build_bot(self, username):
        bot_config = self.bots[username]
        bot = ntelebot.bot.Bot(bot_config['token'])
        bot.config = bot_config
        bot.get_modconf = lambda modname: self.get_modconf(username, modname)
        bot.multibot = self
        bot.username = username
        return bot

    def run_bot(self, username):
        """Begin polling for updates for the previously configured bot."""

        bot = self._build_bot(username)
        self.loop.add(bot, self.dispatcher)
        bot.config['running'] = True
        self.save()

    def stop_bot(self, username):
        """Stop polling for updates for the referenced bot."""

        bot_config = self.bots[username]
        self.loop.remove(bot_config['token'])
        bot_config['running'] = False
        self.save()

    def get_modconf(self, username, modname):
        """Get or create a module config dict."""

        if modname not in self.bots[username]['modules']:
            self.bots[username]['modules'][modname] = {}
        return self.bots[username]['modules'][modname]

    def save(self):
        """Save the list of bots currently being managed to disk."""

        if self.fname:
            self.bots = util.json.dump(self.fname, self.bots)

    def run(self):
        """Begin waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.run()

    def stop(self):
        """Stop waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.stop()
