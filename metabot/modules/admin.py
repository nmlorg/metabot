"""Manage the admin list."""

from __future__ import absolute_import, division, print_function, unicode_literals

import uuid

BOOTSTRAP_TOKEN = uuid.uuid4().hex


def modhelp(ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    bots = sorted(username for username, botconf in ctx.bot.multibot.conf['bots'].items()
                  if ctx.user['id'] in botconf['issue37']['admin']['admins'])

    if bots:
        sections['commands'].add('/admin \u2013 Manage the admin list')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query'):
        if ctx.command == 'admin':
            return default(ctx, msg)
        if ctx.command == '_bootstrap':
            return bootstrap(ctx, msg, modconf)

    return False


def default(ctx, msg):  # pylint: disable=missing-docstring
    ctx.private = True
    bots = sorted(username for username, botconf in ctx.bot.multibot.conf['bots'].items()
                  if ctx.user['id'] in botconf['issue37']['admin']['admins'])

    if not bots:
        return msg.add(
            "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by "
            'opening a chat with me (@%s) and typing:\n'
            '\n'
            '<pre>/admin %s admin add %s</pre>', ctx.bot.username, ctx.bot.username, ctx.user['id'])

    msg.path('/admin', 'Bot Admin')

    username, modname, text = ctx.split(3)
    #if not username and len(bots) == 1:
    #    username = bots[0]

    if username not in bots:
        msg.action = 'Choose a bot'
        for username in bots:
            msg.button(username, '/admin ' + username)
        return

    msg.path(username)

    modules = {
        modname: module
        for modname, module in ctx.bot.multibot.modules.items()
        if hasattr(module, 'admin')
    }

    if not modules:
        return msg.add(
            "Hi! There aren't any configurable modules installed. Contact a metabot admin to "
            'install one.')

    #if not modname and len(modules) == 1:
    #    modname = list(modules)[0]

    if modname not in modules:
        msg.action = 'Choose a module'
        for modname, module in sorted(modules.items()):
            label = modname
            if getattr(module, '__doc__', None):
                label = '%s \u2022 %s' % (label, module.__doc__.splitlines()[0].rstrip('.'))
            msg.button(label, '/admin %s %s' % (username, modname))
        return

    msg.path(modname)

    admin_callback = modules[modname].admin
    ctx.command = 'admin %s %s' % (username, modname)
    ctx.text = text
    return admin_callback(ctx, msg, ctx.bot.multibot.conf['bots'][username]['issue37'][modname])


def bootstrap(ctx, msg, modconf):
    """Add the user who sent the command to the current bot's admin list."""

    if ctx.text == BOOTSTRAP_TOKEN and not modconf['admins']:
        modconf['admins'] = [ctx.user['id']]
        msg.add('Added %s to the admin list.', ctx.user['id'])


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME admin (configure the admin module itself)."""

    if 'admins' not in modconf:
        modconf['admins'] = []

    target = ctx.text
    if target.isdigit():
        target = int(target)
    elif target:
        msg.add("I'm not sure what <code>%s</code> is\u2014it's not a user id!", target)
        target = None

    if not target:
        target = ctx.forward_from

    if target in modconf['admins']:
        if target == ctx.user['id']:
            msg.add("You can't remove yourself from the admin list.")
        else:
            modconf['admins'].remove(target)
            msg.add('Removed %s from the admin list.', target)
    elif target:
        modconf['admins'].append(target)
        modconf['admins'].sort()
        msg.add('Added %s to the admin list.', target)

    msg.action = 'Choose an admin'
    msg.add('Forward a message from a user to add or remove them, or select an existing admin to '
            'remove.')

    for admin_id in sorted(modconf['admins']):
        if admin_id != ctx.user['id']:
            userinfo = ctx.bot.multibot.conf['users'].get(admin_id)
            if userinfo:
                userstr = '%s (%s)' % (userinfo['name'], admin_id)
            else:
                userstr = '%s' % admin_id
            msg.button('Remove ' + userstr, '%s' % admin_id)
