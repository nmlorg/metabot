"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

import ntelebot
import pytest

from metabot.modules import admin
from metabot.modules import globalrecords
from metabot.modules import help  # pylint: disable=redefined-builtin
from metabot import multibot


class BotConversation(object):  # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, *modules):

        def dummymod(ctx):  # pylint: disable=missing-docstring,unused-argument
            return ctx.command == 'dummymod' and ctx.reply_text('DUMMYMOD')

        self.multibot = multibot.MultiBot(set(modules) | {admin, dummymod, globalrecords, help})
        ntelebot.bot.Bot('1234:test').getme.respond(json={
            'ok': True,
            'result': {
                'username': 'modulestestbot'
            },
        })
        username = self.multibot.add_bot('1234:test')
        self.bot = self.multibot._build_bot(username)  # pylint: disable=protected-access
        self.multibot.conf['bots']['modulestestbot']['admin']['admins'] = [1000]

    def inline(self, text, user_id=1000):
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
    def message(self, text, user_id=1000, chat_type='private', last_name=None, language_code=None):
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


@pytest.fixture
def build_conversation():  # pylint: disable=missing-docstring
    return BotConversation
