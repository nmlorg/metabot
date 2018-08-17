"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

import ntelebot
import pytest


class MockMultiBot(object):
    # pylint: disable=missing-docstring,too-few-public-methods

    @staticmethod
    def save():
        pass


class BotConversation(object):  # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, dispatcher):
        self.bot = ntelebot.bot.Bot('modules:test')
        self.bot.config = {'modules': {}, 'username': 'modulestestbot'}
        self.bot.multibot = MockMultiBot()
        self.preprocessor = ntelebot.preprocess.Preprocessor()
        self.preprocessor.bots[self.bot.token] = {'username': 'modulestestbot'}
        self.dispatcher = dispatcher

    def __call__(self, text, user_id=1000, chat_type='private'):
        user = {'id': user_id}
        if chat_type == 'private':
            chat = {'id': user_id, 'type': chat_type}
        else:
            chat = {'id': -user_id, 'type': 'supergroup'}
        message = {'from': user, 'chat': chat, 'message_id': user_id * 2, 'text': text}
        update = {'message': message}
        ctx = self.preprocessor(self.bot, update)
        responses = []

        def _handler(request, unused_context):
            responses.append(json.loads(request.body))
            return {'ok': True, 'result': {}}

        self.bot.send_message.respond(json=_handler)
        self.dispatcher(ctx)
        return responses


@pytest.fixture
def build_conversation():  # pylint: disable=missing-docstring
    return BotConversation
