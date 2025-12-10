"""Test environment defaults."""

import functools
import json
import zlib

import ntelebot
from ntelebot.conftest import _bot_mock  # pylint: disable=unused-import
import pytest

from metabot.modules import admin
from metabot.modules import help  # pylint: disable=redefined-builtin
from metabot import multibot


@pytest.fixture(autouse=True)
def _dont_mangle_callback_data(monkeypatch):
    monkeypatch.setattr('ntelebot.keyboardutil.fix', lambda keyboard, maxlen=0: None)


@pytest.fixture(autouse=True)
def _dont_mangle_invisible_links(monkeypatch):

    def _encode(btn, meta):
        text = ''
        if btn:
            text = f"{text}[btn {' '.join(map(repr, btn))}]\n"
        if meta:
            text = f"{text}[meta {' '.join(f'{k}={repr(v)}' for k, v in meta.items())}]\n"
        return text

    monkeypatch.setattr('ntelebot.invislink.encode', _encode)


@pytest.fixture(autouse=True)
def _disable_geoutil(monkeypatch):
    monkeypatch.setattr('metabot.util.geoutil._CLIENT', None)


def _format_dict(data):
    if isinstance(data, dict):
        data = [f'{field}={_format_dict(value)}' for field, value in sorted(data.items())]
    if isinstance(data, list):
        return f"[{' '.join(map(_format_dict, data))}]"
    return data


def _format_message(response):
    method = response.pop('method')
    text = response.pop('text', None) or response.pop('caption', None)
    if not text and (media := response.get('media')):
        num_captions = sum('caption' in medium and 1 or 0 for medium in media)
        if num_captions == 1:
            text = media[0].pop('caption', None) or media[-1].pop('caption', None)
    if not text:
        text = '(EMPTY MESSAGE)'
    reply_markup = response.pop('reply_markup', None)
    header = _format_dict(response)
    if method != 'send_message':
        header = f'[{method} {header[1:]}'
    text = f'{header}\n{text}\n'
    if reply_markup:
        for row in reply_markup.pop('inline_keyboard', ()):
            text = '%s%s\n' % (text, ' '.join(
                '[%s | %s]' % (button['text'], button['callback_data']) for button in row))
        if reply_markup:  # pragma: no cover
            text = '%s%s\n' % (text, json.dumps(reply_markup, sort_keys=True))
    return text


class BotConversation:  # pylint: disable=missing-docstring,too-few-public-methods

    def __init__(self, *modules):

        def dummymod(ctx):  # pylint: disable=missing-docstring
            return ctx.command == 'dummymod' and ctx.reply_text('DUMMYMOD')

        self.multibot = multibot.MultiBot(set(modules) | {admin, dummymod, help})
        self.set_bot('modulestestbot')
        self.mgr.bot_admins = [1000]
        self.last_message_id = 12344

    def set_bot(self, botuser):
        assert botuser not in self.multibot.conf['bots']
        bot_id = 100000000 + zlib.crc32(botuser.encode('ascii'))
        bot_token = f'{bot_id}:valid-for-{botuser}'
        ntelebot.bot.Bot(bot_token).getme.respond(json={
            'ok': True,
            'result': {
                'username': botuser,
            },
        })
        assert self.multibot.add_bot(bot_token) == botuser
        self.mgr = self.multibot.mgr.bot(botuser)
        self.bot = self.mgr.bot_api

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
                    *,
                    user_id=1000,
                    chat_type='private',
                    forward_date=None,
                    forward_from=None):
        """Simulate a private message."""

        user = {'id': user_id, 'username': 'user%s' % user_id, 'first_name': 'User%s' % user_id}
        if chat_type == 'private':
            chat = {'id': user_id, 'type': 'private'}
        else:
            chat = {'id': -1001000000000 - user_id, 'type': chat_type, 'title': 'Group Chat'}
        if chat_type == 'channel':
            channel_post = {
                'author_signature': user['first_name'],
                'chat': chat,
                'message_id': user_id * 2,
                'text': text,
            }
            update = {'channel_post': channel_post}
        else:
            message = {'from': user, 'chat': chat, 'message_id': user_id * 2, 'text': text}
            if forward_date:
                message['forward_date'] = forward_date
            if forward_from:
                message['forward_from'] = {'id': forward_from}
            update = {'message': message}

        responses = []

        def _handler(method, request, unused_context):
            response = json.loads(request.body.decode('ascii'))
            response['method'] = method
            responses.append(response)
            if method.startswith('edit_'):
                message_id = response['message_id']
            else:
                self.last_message_id += 1
                message_id = self.last_message_id
            message = {'chat': {'id': int(response['chat_id'])}, 'message_id': message_id}
            if response.get('caption'):
                message['caption'] = 'CAPTION'
            return {'ok': True, 'result': message}

        def _send_media_group(request, unused_context):
            response = json.loads(request.body.decode('ascii'))
            response['method'] = 'send_media_group'
            responses.append(response)
            messages = []
            for media in response['media']:
                self.last_message_id += 1
                message_id = self.last_message_id
                message = {'chat': {'id': int(response['chat_id'])}, 'message_id': message_id}
                if media.get('caption'):
                    message['caption'] = 'CAPTION'
                messages.append(message)
            return {'ok': True, 'result': messages}

        for method in ('edit_message_caption', 'edit_message_text', 'forward_message',
                       'pin_chat_message', 'send_message', 'send_photo', 'unpin_chat_message'):
            getattr(self.bot, method).respond(json=functools.partial(_handler, method))
        self.bot.send_media_group.respond(json=_send_media_group)
        self.multibot.dispatcher(self.bot, update)
        return responses

    # pylint: enable=too-many-arguments

    @staticmethod
    def format_messages(messages):
        """Format a sequence of intercepted API calls into a transcript representation."""

        return '\n\n'.join(map(_format_message, messages))

    def message(self, *args, **kwargs):
        """Simulate a private message (with human-friendly output)."""

        return self.format_messages(self.raw_message(*args, **kwargs))


@pytest.fixture
def build_conversation():  # pylint: disable=missing-docstring
    return BotConversation
