"""Simple context manager."""

import ntelebot

from metabot.util import dicttools


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

    def bot(self, bot_id):
        bot_id, bot_username = self._normalize_bot_id(bot_id)
        return Manager(self, bot_id=bot_id, bot_username=bot_username)

    @property
    def bot_conf(self):
        return self.multibot.conf['bots'][self.bot_username]['issue37']

    @property
    def bot_instance(self):
        """The shared instance of ntelebot.bot.Bot(self.bot_token)."""

        if (bot := self._bot_instances.get(self.bot_id)):
            return bot

        self._bot_instances[self.bot_id] = bot = ntelebot.bot.Bot(self.bot_token)
        bot._username = self.bot_username  # pylint: disable=protected-access
        bot.config = self.multibot.conf['bots'][bot.username]
        return bot

    @property
    def bot_token(self):
        return self.bot_conf['telegram']['token']

    def chat(self, chat_id):
        return Manager(self, chat_id=int(chat_id))

    @property
    def chat_admins(self):
        return self.chat_info.get('admins', ())

    @property
    def chat_info(self):
        return self.multibot.conf['groups'][self.chat_id]

    @property
    def chat_pinned_message_id(self):
        return self.chat_info.get('pinned_message_id')

    @property
    def chat_title(self):
        return self.chat_info.get('title')

    @property
    def chat_username(self):
        return self.chat_info.get('username')

    def user(self, user_id):
        return Manager(self, user_id=int(user_id))

    @property
    def user_info(self):
        return self.multibot.conf['users'][self.user_id]

    @property
    def user_name(self):
        return self.user_info.get('name')

    @property
    def user_username(self):
        return self.user_info.get('username')

    @property
    def is_chat_admin(self):
        return self.user_id in self.chat_admins
