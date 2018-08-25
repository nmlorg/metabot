"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

import ntelebot
import pytest

from metabot.modules import admin
from metabot import multibot


class BotConversation(object):  # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, module):

        def dummymod(ctx):  # pylint: disable=missing-docstring,unused-argument
            return ctx.command == 'dummymod' and ctx.reply_text('DUMMYMOD')

        self.multibot = multibot.MultiBot({admin, dummymod, module})
        ntelebot.bot.Bot('1234:test').getme.respond(json={
            'ok': True,
            'result': {
                'username': 'modulestestbot'
            },
        })
        username = self.multibot.add_bot('1234:test')
        self.bot = self.multibot._build_bot(username)  # pylint: disable=protected-access
        self.bot.get_modconf('admin')['admins'] = [1000]

    def __call__(self, text, user_id=1000, chat_type='private'):
        user = {'id': user_id}
        if chat_type == 'private':
            chat = {'id': user_id, 'type': chat_type}
        else:
            chat = {'id': -user_id, 'type': 'supergroup'}
        message = {'from': user, 'chat': chat, 'message_id': user_id * 2, 'text': text}
        update = {'message': message}
        responses = []

        def _handler(request, unused_context):
            responses.append(json.loads(request.body))
            return {'ok': True, 'result': {}}

        self.bot.send_message.respond(json=_handler)
        self.multibot.dispatcher(self.bot, update)
        return responses


@pytest.fixture
def build_conversation():  # pylint: disable=missing-docstring
    return BotConversation
