"""Simple context manager."""

import ntelebot

from metabot.util import dicttools
from metabot.util import mandb

F = mandb.Field


class Manager:  # pylint: disable=missing-function-docstring
    """Simple context manager."""

    def __init__(self, root, *, bot_id=None, bot_username=None, chat_id=None, user_id=None):  # pylint: disable=too-many-arguments
        if isinstance(root, Manager):
            self.__dict__.update(root.__dict__)
        else:
            assert isinstance(root.conf, dicttools.ImplicitTrackingDict)
            self.multibot = root
            self._bot_instances = {}

        if bot_id:
            self.bot_id = bot_id
        if bot_username:
            self.bot_username = bot_username
        if chat_id:
            self.chat_id = chat_id
        if user_id:
            self.user_id = user_id

    def _normalize_bot_id(self, bot_id):
        try:
            bot_id = int(bot_id)
        except ValueError:
            pass
        if isinstance(bot_id, int):
            if (bot := self._bot_instances.get(bot_id)):
                bot_username = bot.username
            else:
                for bot_username, conf in self.multibot.conf['bots'].items():
                    if int(conf['issue37']['telegram']['token'].split(':', 1)[0]) == bot_id:
                        break
                else:
                    raise KeyError(bot_id)
        elif bot_id in self.multibot.conf['bots']:
            bot_username = bot_id
            token = self.multibot.conf['bots'][bot_username]['issue37']['telegram']['token']
            bot_id = int(token.split(':', 1)[0])
        else:
            raise KeyError(bot_id)

        return bot_id, bot_username

    @property
    def running_bots(self):
        for botuser in self.multibot.conf['bots']:
            if (mgr := self.bot(botuser)).bot_running:
                yield mgr

    def bot(self, bot_id):
        bot_id, bot_username = self._normalize_bot_id(bot_id)
        return Manager(self, bot_id=bot_id, bot_username=bot_username)

    @property
    def bot_active_groups(self):
        for chat_id in self.bot_conf.get('moderator', ()):
            yield self.chat(chat_id)

    @property
    def bot_api(self):
        """The shared instance of ntelebot.bot.Bot(self.bot_token)."""

        if (bot := self._bot_instances.get(self.bot_id)):
            return bot

        self._bot_instances[self.bot_id] = bot = ntelebot.bot.Bot(self.bot_token)
        bot._username = self.bot_username  # pylint: disable=protected-access
        bot.config = self.multibot.conf['bots'][bot.username]
        return bot

    bot_conf = F(lambda self: self.multibot.conf['bots'][self.bot_username], 'issue37', dict)
    bot_running = F(lambda self: self.bot_conf['telegram'], 'running', bool)
    bot_token = F(lambda self: self.bot_conf['telegram'], 'token', str)

    def chat(self, chat_id):
        return Manager(self, chat_id=int(chat_id))

    chat_admins = F(lambda self: self.chat_info, 'admins', list)
    chat_conf = F(lambda self: self.bot_conf['moderator'], lambda self: f'{self.chat_id}', dict)
    chat_info = F(lambda self: self.multibot.conf['groups'], lambda self: self.chat_id, dict)
    chat_pinned_message_id = F(lambda self: self.chat_info, 'pinned_message_id', int)
    chat_title = F(lambda self: self.chat_info, 'title', str)
    chat_username = F(lambda self: self.chat_info, 'username', str)

    def user(self, user_id):
        return Manager(self, user_id=int(user_id))

    user_conf = F(lambda self: self.bot_conf['events']['users'], lambda self: f'{self.user_id}',
                  dict)
    user_info = F(lambda self: self.multibot.conf['users'], lambda self: self.user_id, dict)
    user_name = F(lambda self: self.user_info, 'name', str)
    user_username = F(lambda self: self.user_info, 'username', str)
    is_chat_admin = F(lambda self: self.chat_admins, lambda self: self.user_id, bool)
