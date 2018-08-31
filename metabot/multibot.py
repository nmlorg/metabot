"""An ntelebot.loop.Loop that manages multiple bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot

from metabot import botconf


class MultiBot(object):
    """An ntelebot.loop.Loop that manages multiple bots."""

    def __init__(self, modules, fname=None):
        self.modules = {}
        self.dispatcher = _MultiBotLoopDispatcher()
        for module in modules:
            modname = module.__name__.rsplit('.', 1)[-1]
            self.modules[modname] = module
        self.loop = ntelebot.loop.Loop()
        self.bots = botconf.BotConf(fname)
        self.bots.finalize()

        for username, bot_config in self.bots.items():
            if bot_config['telegram']['running']:
                self.run_bot(username)

    def add_bot(self, token):
        """Begin polling bot_config.token, dispatching updates through bot_config.modules."""

        bot_info = ntelebot.bot.Bot(token).get_me()
        self.bots[bot_info['username']] = {
            'telegram': {
                'running': False,
                'token': token,
            },
        }
        self.bots.save()
        return bot_info['username']

    def _build_bot(self, username):
        bot_config = self.bots[username]
        bot = ntelebot.bot.Bot(bot_config['telegram']['token'])
        bot.config = bot_config
        bot.multibot = self
        bot.username = username
        return bot

    def run_bot(self, username):
        """Begin polling for updates for the previously configured bot."""

        bot = self._build_bot(username)
        self.loop.add(bot, self.dispatcher)
        bot.config['telegram']['running'] = True
        self.bots.save()

    def stop_bot(self, username):
        """Stop polling for updates for the referenced bot."""

        bot_config = self.bots[username]
        self.loop.remove(bot_config['telegram']['token'])
        bot_config['telegram']['running'] = False
        self.bots.save()

    def run(self):
        """Begin waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.run()

    def stop(self):
        """Stop waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.stop()


class _MultiBotLoopDispatcher(ntelebot.dispatch.LoopDispatcher):

    def __call__(self, bot, update):
        logging.info('%s', update)

        multibot = bot.multibot
        ctx = self.preprocessor(bot, update)

        with multibot.bots.record_mutations(ctx):
            botconfig = multibot.bots[bot.username]

            for modname, module in multibot.modules.items():
                modpredispatch = getattr(module, 'modpredispatch', None)
                if modpredispatch:
                    modpredispatch(ctx, botconfig[modname])

            ret = False
            for modname, module in multibot.modules.items():
                dispatch = ntelebot.dispatch.get_callback(module)
                if dispatch:
                    ret = dispatch(ctx)
                    if ret is not False:
                        break

                moddispatch = getattr(module, 'moddispatch', None)
                if moddispatch:
                    ret = moddispatch(ctx, botconfig[modname])
                    if ret is not False:
                        break

            for modname, module in multibot.modules.items():
                modpostdispatch = getattr(module, 'modpostdispatch', None)
                if modpostdispatch:
                    modpostdispatch(ctx, botconfig[modname])

            return ret
