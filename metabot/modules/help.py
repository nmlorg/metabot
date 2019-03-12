"""Return the list of commands and other bot features."""

from __future__ import absolute_import, division, print_function, unicode_literals

import collections

ALIASES = ('command', 'commands', 'help', 'start')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command in ALIASES:
        return default(ctx, msg, modconf)

    return False


def default(ctx, msg, modconf):  # pylint: disable=missing-docstring
    ctx.private = True
    sections = collections.defaultdict(set)

    hidden = set(modconf.get('hidden', '').split())

    for modname, module in ctx.bot.multibot.modules.items():
        if modname in hidden:
            continue
        modhelp = getattr(module, 'modhelp', None)
        if modhelp:
            modhelp(ctx, ctx.bot.multibot.conf['bots'][ctx.bot.username]['issue37'][modname],
                    sections)

    if not sections:
        msg.add("I don't have much documentation\u2014check with a bot admin!")
    else:
        for name, lines in sorted(sections.items()):
            msg.add('<b>%s</b>', name.title())
            for line in sorted(lines):
                msg.add('%s', line)


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME help."""

    action, modname = ctx.split(2)

    hidden = set(modconf.get('hidden', '').split())

    if action == 'hide':
        if modname in hidden:
            msg.add('<code>%s</code> is already hidden!', modname)
        else:
            msg.add('<code>%s</code> is now hidden.', modname)
            hidden.add(modname)
    elif action == 'unhide':
        if modname not in hidden:
            msg.add('<code>%s</code> is not hidden!', modname)
        else:
            msg.add('<code>%s</code> is now visible.', modname)
            hidden.remove(modname)

    if hidden:
        modconf['hidden'] = ' '.join(sorted(hidden))
    else:
        modconf.pop('hidden')

    modules = collections.defaultdict(lambda: collections.defaultdict(set))
    for modname, module in ctx.bot.multibot.modules.items():
        modhelp = getattr(module, 'modhelp', None)
        if modhelp:
            modhelp(ctx, ctx.bot.multibot.conf['bots'][ctx.bot.username]['issue37'][modname],
                    modules[modname])

    msg.action = 'Select a module'
    for modname, sections in sorted(modules.items()):
        label = '%s (%s)' % (modname, ' \u2022 '.join(sorted(sections['commands'])))
        if modname in hidden:
            msg.button('Show ' + label, 'unhide ' + modname)
        elif sections:
            msg.button('Hide ' + label, 'hide ' + modname)
