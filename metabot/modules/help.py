"""Return the list of commands and other bot features."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections

from metabot import util

ALIASES = ('command', 'commands', 'help', 'start')


def dispatch(ctx):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        ctx.private = True
        return default(ctx)

    return False


def default(ctx):  # pylint: disable=missing-docstring
    msg = util.msgbuilder.MessageBuilder()

    sections = collections.defaultdict(set)

    for modname, module in ctx.bot.multibot.modules.items():
        modhelp = getattr(module, 'modhelp', None)
        if modhelp:
            modhelp(ctx, ctx.bot.multibot.bots[ctx.bot.username][modname], sections)

    if not sections:
        msg.add("I don't have much documentation\u2014check with a bot admin!")
    else:
        for name, lines in sorted(sections.items()):
            msg.add('<b>%s</b>', name.title())
            for line in sorted(lines):
                msg.add('%s', line)

    return msg.reply(ctx)
