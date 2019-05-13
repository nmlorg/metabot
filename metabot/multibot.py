"""An ntelebot.loop.Loop that manages multiple bots."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import ntelebot

from metabot import botconf
from metabot import datasettings
from metabot.calendars import multicalendar
from metabot.util import jsonutil
from metabot.util import msgbuilder


class MultiBot(object):
    """An ntelebot.loop.Loop that manages multiple bots."""

    def __init__(self, modules, confdir=None):
        self.dispatcher = _MultiBotLoopDispatcher()
        self.loop = ntelebot.loop.Loop()
        self.conf = botconf.BotConf(confdir)
        self.conf.finalize()
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

        for username, bot_config in self.conf['bots'].items():
            if bot_config['issue37']['telegram']['running']:
                self.run_bot(username)

    def add_bot(self, token):
        """Begin polling bot_config.token, dispatching updates through bot_config.modules."""

        username = ntelebot.bot.Bot(token).username
        self.conf['bots'][username] = {
            'issue37': {
                'telegram': {
                    'running': False,
                    'token': token,
                },
            },
        }
        self.conf.save()
        return username

    def _build_bot(self, username):
        bot_config = self.conf['bots'][username]
        bot = ntelebot.bot.Bot(bot_config['issue37']['telegram']['token'])
        bot.config = bot_config
        bot.multibot = self
        assert bot.username == username
        return bot

    def run_bot(self, username):
        """Begin polling for updates for the previously configured bot."""

        bot = self._build_bot(username)
        self.loop.add(bot, self.dispatcher)
        bot.config['issue37']['telegram']['running'] = True
        self.conf.save()

    def stop_bot(self, username):
        """Stop polling for updates for the referenced bot."""

        bot_config = self.conf['bots'][username]
        self.loop.remove(bot_config['issue37']['telegram']['token'])
        bot_config['issue37']['telegram']['running'] = False
        self.conf.save()

    def run(self):
        """Begin waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.run()

    def stop(self):
        """Stop waiting for and dispatching updates sent to any bot currently running."""

        return self.loop.stop()


class _MultiBotLoopDispatcher(ntelebot.dispatch.LoopDispatcher):

    def __call__(self, bot, update):  # pylint: disable=too-many-branches,too-many-locals
        logging.info('%s', _pretty_repr(update))

        multibot = bot.multibot
        ctx = self.preprocessor(bot, update)
        if not ctx:
            return False

        with multibot.conf.record_mutations(ctx):
            botconfig = multibot.conf['bots'][bot.username]
            msg = msgbuilder.MessageBuilder()

            ctx.botinfo = datasettings.DataSettings(botconfig['data'], botconfig['settings'])

            if not ctx.user:
                ctx.userinfo = None
            else:
                ctx.userinfo = datasettings.DataSettings(multibot.conf['users'][ctx.user['id']],
                                                         botconfig['users'][ctx.user['id']])
                for k, val in ctx.user.items():
                    if k not in ('first_name', 'id', 'last_name'):
                        ctx.userinfo.data[k] = val
                    ctx.userinfo.data.name = (
                        '%s %s' %
                        (ctx.user.get('first_name', ''), ctx.user.get('last_name', ''))).strip()

            if not ctx.chat or ctx.chat['type'] not in ('channel', 'group', 'supergroup'):
                ctx.groupinfo = None
            else:
                ctx.groupinfo = datasettings.DataSettings(multibot.conf['groups'][ctx.chat['id']],
                                                          botconfig['groups'][ctx.chat['id']])
                for k, val in ctx.chat.items():
                    if k != 'id':
                        ctx.groupinfo.data[k] = val

                if ctx.type == 'pin':
                    ctx.groupinfo.data.pinned_message_id = ctx.data['message_id']

            for modname, module in multibot.modules.items():
                modpredispatch = getattr(module, 'modpredispatch', None)
                if modpredispatch:
                    modpredispatch(ctx, msg, botconfig['issue37'][modname])

            ret = False
            for modname, module in multibot.modules.items():
                dispatch = ntelebot.dispatch.get_callback(module)
                if dispatch:
                    ret = dispatch(ctx)
                    if ret is not False:
                        break

                moddispatch = getattr(module, 'moddispatch', None)
                if moddispatch:
                    ret = moddispatch(ctx, msg, botconfig['issue37'][modname])
                    if ret is not False:
                        break

            for modname, module in multibot.modules.items():
                modpostdispatch = getattr(module, 'modpostdispatch', None)
                if modpostdispatch:
                    modpostdispatch(ctx, msg, botconfig['issue37'][modname])

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
