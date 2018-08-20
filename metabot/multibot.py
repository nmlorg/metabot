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
            self.dispatcher.add(build_dispatcher(modname, module))
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
        bot.username = username
        bot.config = bot_config
        bot.multibot = self
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

    def enable_module(self, username, modname, command=None):
        """Enable the modname module under /command (or /modname)."""

        bot_config = self.bots[username]
        if modname not in bot_config['modules']:
            bot_config['modules'][modname] = {}
        if 'commands' not in bot_config['modules'][modname]:
            bot_config['modules'][modname]['commands'] = []
        bot_config['modules'][modname]['commands'].append(command or modname)
        bot_config['modules'][modname]['commands'].sort()
        self.save()

    def disable_module(self, username, modname, command=None):
        """Disable the modname module under /command (or /modname)."""

        bot_config = self.bots[username]
        if modname not in bot_config['modules']:
            return
        if 'commands' not in bot_config['modules'][modname]:
            return
        if not command:
            command = modname
        if command not in bot_config['modules'][modname]['commands']:
            return
        if len(bot_config['modules'][modname]['commands']) == 1:
            bot_config['modules'][modname].pop('commands')
            if not bot_config['modules'][modname]:
                bot_config['modules'].pop(modname)
        else:
            bot_config['modules'][modname]['commands'].remove(command)
        self.save()

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


def build_dispatcher(modname, module):
    """Build a dispatcher that checks incoming commands against the per-bot module config."""

    callback = ntelebot.dispatch.get_callback(module)

    def _dispatch(ctx):
        if ctx.type not in ('message', 'callback_query') or not ctx.command:
            return False
        mod_config = ctx.bot.config['modules'].get(modname)
        if (not mod_config or not mod_config.get('commands') or
                ctx.command not in mod_config['commands']):
            return False
        return callback(ctx)

    return _dispatch
