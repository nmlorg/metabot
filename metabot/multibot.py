"""An ntelebot.loop.Loop that manages multiple bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot

from metabot import util


class MultiBot(object):
    """An ntelebot.loop.Loop that manages multiple bots."""

    fname = 'config/multibot.json'

    def __init__(self, modules):
        self.modules = modules
        self.loop = ntelebot.loop.Loop()
        self.bots = []

        bots = util.json.load(self.fname)
        if bots and isinstance(bots, list):
            for bot_config in bots:
                self.add_bot(bot_config)

    def add_bot(self, bot_config):
        """Begin polling bot_config.token, dispatching updates through bot_config.modules."""

        bot = ntelebot.bot.Bot(bot_config['token'])
        try:
            bot_info = bot.get_me()
        except ntelebot.errors.Error as exc:
            logging.error('Unable to add %r: %s', bot.token, exc)
            return
        bot_config['id'] = bot_info['id']
        bot_config['username'] = bot_info['username']
        bot.config = bot_config
        bot.multibot = self
        dispatcher = ntelebot.dispatch.LoopDispatcher()
        for modname in bot_config['modules']:
            dispatcher.add_command(modname, self.modules[modname])
        self.bots.append(bot_config)
        self.loop.add(bot, dispatcher)

    def save(self):
        """Save the list of bots currently being managed to disk."""

        self.bots = util.json.dump(self.fname, self.bots)

    def run(self):
        """Begin waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.run()
