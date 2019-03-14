"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

import ntelebot
from ntelebot.conftest import _bot_mock  # pylint: disable=unused-import
import pytest

from metabot.modules import admin
from metabot.modules import help  # pylint: disable=redefined-builtin
from metabot.modules import settings
from metabot import multibot


@pytest.fixture(autouse=True)
def _dont_mangle_callback_data(monkeypatch):
    monkeypatch.setattr('ntelebot.keyboardutil.fix', lambda keyboard, maxlen=0: None)


def _format_message(response):
    text = response.pop('text', '(EMPTY MESSAGE)')
    reply_markup = response.pop('reply_markup', None)
    header = ' '.join('%s=%s' % (field, value) for field, value in sorted(response.items()))
    text = '[%s]\n%s\n' % (header, text)
    if reply_markup:
        for row in reply_markup.pop('inline_keyboard', ()):
            text = '%s%s\n' % (text, ' '.join(
                '[%s | %s]' % (button['text'], button['callback_data']) for button in row))
        if reply_markup:  # pragma: no cover
            text = '%s%s\n' % (text, json.dumps(reply_markup, sort_keys=True))
    return text


class BotConversation(object):  # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, *modules):

        def dummymod(ctx):  # pylint: disable=missing-docstring,unused-argument
            return ctx.command == 'dummymod' and ctx.reply_text('DUMMYMOD')

        self.multibot = multibot.MultiBot(set(modules) | {admin, dummymod, help, settings})
        ntelebot.bot.Bot('1234:test').getme.respond(json={
            'ok': True,
            'result': {
                'username': 'modulestestbot'
            },
        })
        username = self.multibot.add_bot('1234:test')
        self.bot = self.multibot._build_bot(username)  # pylint: disable=protected-access
        self.multibot.conf['bots']['modulestestbot']['issue37']['admin']['admins'] = [1000]

    def raw_inline(self, text, user_id=1000):
        """Simulate an inline query (@BOTNAME text)."""

        user = {'id': user_id}
        inline_query = {'offset': '', 'from': user, 'query': text, 'id': user_id * 2}
        update = {'inline_query': inline_query}
        responses = []

        def _handler(request, unused_context):
            responses.append(json.loads(request.body.decode('ascii')))
            return {'ok': True, 'result': {}}

        self.bot.answer_inline_query.respond(json=_handler)
        self.multibot.dispatcher(self.bot, update)
        return responses

    # pylint: disable=too-many-arguments
    def raw_message(self,
                    text,
                    user_id=1000,
                    chat_type='private',
                    last_name=None,
                    language_code=None):
        """Simulate a private message."""

        user = {'id': user_id, 'username': 'user%s' % user_id, 'first_name': 'User%s' % user_id}
        if last_name:
            user['last_name'] = last_name
        if language_code:
            user['language_code'] = language_code
        if chat_type == 'private':
            chat = {'id': user_id, 'type': 'private'}
        else:
            chat = {'id': -1001000000000 - user_id, 'type': chat_type, 'title': 'Group Chat'}
        message = {'from': user, 'chat': chat, 'message_id': user_id * 2, 'text': text}
        update = {'message': message}
        responses = []

        def _handler(request, unused_context):
            responses.append(json.loads(request.body.decode('ascii')))
            return {'ok': True, 'result': {}}

        self.bot.send_message.respond(json=_handler)
        self.multibot.dispatcher(self.bot, update)
        return responses

    def message(self, *args, **kwargs):
        """Simulate a private message (with human-friendly output)."""

        return '\n\n'.join(
            _format_message(response) for response in self.raw_message(*args, **kwargs))


@pytest.fixture
def build_conversation():  # pylint: disable=missing-docstring
    return BotConversation
