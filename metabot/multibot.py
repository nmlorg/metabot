"""An ntelebot.loop.Loop that manages multiple bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot

from metabot import botconf
from metabot.calendars import multicalendar
from metabot.util import jsonutil
from metabot.util import msgbuilder


class MultiBot(object):
    """An ntelebot.loop.Loop that manages multiple bots."""

    def __init__(self, modules, confdir=None):
        self.dispatcher = _MultiBotLoopDispatcher()
        self.loop = ntelebot.loop.Loop()
        self.bots = botconf.BotConf(confdir)
        self.bots.finalize()
        self.multical = multicalendar.MultiCalendar()
        self.calendars = {}
        if confdir:
            for calendar_info in jsonutil.load(confdir + '/calendars.json') or ():
                cal = self.multical.add(calendar_info['calid'])
                self.calendars[cal.calcode] = calendar_info
        self.modules = {}
        for module in modules:
            modname = module.__name__.rsplit('.', 1)[-1]
            self.modules[modname] = module
            modinit = getattr(module, 'modinit', None)
            if modinit:
                modinit(self)

        for username, bot_config in self.bots.items():
            if bot_config['telegram']['running']:
                self.run_bot(username)

    def add_bot(self, token):
        """Begin polling bot_config.token, dispatching updates through bot_config.modules."""

        username = ntelebot.bot.Bot(token).username
        self.bots[username] = {
            'telegram': {
                'running': False,
                'token': token,
            },
        }
        self.bots.save()
        return username

    def _build_bot(self, username):
        bot_config = self.bots[username]
        bot = ntelebot.bot.Bot(bot_config['telegram']['token'])
        bot.config = bot_config
        bot.multibot = self
        assert bot.username == username
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
        logging.info('%s', _pretty_repr(update))

        multibot = bot.multibot
        ctx = self.preprocessor(bot, update)
        if not ctx:
            return False

        with multibot.bots.record_mutations(ctx):
            botconfig = multibot.bots[bot.username]
            msg = msgbuilder.MessageBuilder()

            for modname, module in multibot.modules.items():
                modpredispatch = getattr(module, 'modpredispatch', None)
                if modpredispatch:
                    modpredispatch(ctx, msg, botconfig[modname])

            ret = False
            for modname, module in multibot.modules.items():
                dispatch = ntelebot.dispatch.get_callback(module)
                if dispatch:
                    ret = dispatch(ctx)
                    if ret is not False:
                        break

                moddispatch = getattr(module, 'moddispatch', None)
                if moddispatch:
                    ret = moddispatch(ctx, msg, botconfig[modname])
                    if ret is not False:
                        break

            for modname, module in multibot.modules.items():
                modpostdispatch = getattr(module, 'modpostdispatch', None)
                if modpostdispatch:
                    modpostdispatch(ctx, msg, botconfig[modname])

            if msg:
                msg.reply(ctx)

            return ret


def _pretty_repr(obj):
    if isinstance(obj, dict):
        return '{%s}' % ', '.join(
            '\033[31m%s\033[0m=%s' % (k, _pretty_repr(v)) for k, v in sorted(obj.items()))
    if isinstance(obj, (list, tuple)):
        return '[%s]' % ', '.join(map(_pretty_repr, obj))
    return '\033[32;1m%s\033[0m' % repr(obj)
