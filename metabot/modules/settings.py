"""Main configuration interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from metabot.util import httpserver


def moddispatch(ctx, msg, unused_modconf):  # pylint: disable=missing-docstring
    if ctx.botinfo.settings.httpserver and not getattr(ctx.bot.multibot, 'settings_httpserver',
                                                       None):
        ctx.bot.multibot.settings_httpserver = httpserver.HTTPServer(ctx.bot.multibot)
        ctx.bot.multibot.settings_httpserver.serve_forever_in_thread()
        logging.info('Settings Web UI running on http://127.0.0.1:%i/.',
                     ctx.bot.multibot.settings_httpserver.server_port)

    if ctx.type in ('message', 'callback_query'):
        if ctx.command in ('set', 'settings'):
            return default(ctx, msg)

    return False


def default(ctx, msg):  # pylint: disable=missing-docstring
    ctx.private = True
    if getattr(ctx.bot.multibot, 'settings_httpserver', None):
        msg.add('<a href="http://127.0.0.1:%s/">Settings Web UI</a>',
                ctx.bot.multibot.settings_httpserver.server_port)
    msg.add('See <a href="https://github.com/nmlorg/metabot/issues/37">metabot issue #37</a>.')
