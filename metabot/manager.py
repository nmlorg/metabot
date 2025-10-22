"""Simple context manager."""

import ntelebot

from metabot.util import dicttools


class Manager:
    """Simple context manager."""

    _bot = None

    def __init__(self, root, **extra):
        if isinstance(root, Manager):
            self.__dict__.update(root.__dict__)
        else:
            assert isinstance(root.conf, dicttools.ImplicitTrackingDict)
            self.multibot = root
            self._bot_instances = {}

        self.__dict__.update(extra)

    def bot(self, bot_id):
        """Return a Manager with the given bot as its bot context."""

        return Manager(self, _bot=_Bot(self, bot_id))

    def __getattribute__(self, key):
        for prefix in ('bot',):
            if key.startswith(prefix + '_'):
                return getattr(super().__getattribute__('_' + prefix), key[len(prefix) + 1:])
        return super().__getattribute__(key)


class _Bot:

    def __init__(self, mgr, bot_id):
        self._mgr = mgr
        try:
            bot_id = int(bot_id)
        except ValueError:
            pass
        if isinstance(bot_id, int):
            self.id = bot_id
            if (bot := self._mgr._bot_instances.get(self.id)):
                self.username = bot.username
            else:
                for username, conf in self._mgr.multibot.conf['bots'].items():
                    if int(conf['issue37']['telegram']['token'].split(':', 1)[0]) == bot_id:
                        self.username = username
                        break
                else:
                    raise KeyError(bot_id)
        elif bot_id in self._mgr.multibot.conf['bots']:
            self.username = bot_id
            self.id = int(self.token.split(':', 1)[0])
        else:
            raise KeyError(bot_id)

    @property
    def conf(self):  # pylint: disable=missing-function-docstring
        return self._mgr.multibot.conf['bots'][self.username]['issue37']

    @property
    def instance(self):
        """The shared instance of ntelebot.bot.Bot(self.token)."""

        # pylint: disable=protected-access # https://github.com/pylint-dev/pylint/issues/4362
        if (bot := self._mgr._bot_instances.get(self.id)):
            return bot

        self._mgr._bot_instances[self.id] = bot = ntelebot.bot.Bot(self.token)
        bot._username = self.username
        bot.multibot = self._mgr.multibot
        bot.config = bot.multibot.conf['bots'][bot.username]
        return bot

    @property
    def token(self):  # pylint: disable=missing-function-docstring
        return self.conf['telegram']['token']
