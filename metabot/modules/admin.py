"""Manage the bot's state and settings."""

from __future__ import absolute_import, division, print_function, unicode_literals


def modhelp(ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    bots = sorted(username for username, botconf in ctx.bot.multibot.bots.items()
                  if ctx.user['id'] in botconf['admin']['admins'])

    if bots:
        sections['commands'].add("/admin \u2013 Manage the bot's state and settings")


def moddispatch(ctx, msg, unused_modconf):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command == 'admin':
        return default(ctx, msg)

    return False


def default(ctx, msg):  # pylint: disable=missing-docstring
    ctx.private = True
    bots = sorted(username for username, botconf in ctx.bot.multibot.bots.items()
                  if ctx.user['id'] in botconf['admin']['admins'])

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
    return admin_callback(ctx, msg, ctx.bot.multibot.bots[username][modname])


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME admin (configure the admin module itself)."""

    action, target = ctx.split(2)

    msg.action = 'Choose an admin'
    msg.add(
        'Type the user id (a number like <code>431603199</code>) of the user to add as an admin, '
        'or select an existing admin to remove.')

    if 'admins' not in modconf:
        modconf['admins'] = []

    if action == 'add':
        if not target.isdigit():
            msg.add("I'm not sure what <code>%s</code> is\u2014it's not a user id!", target)
        else:
            target = int(target)
            if target in modconf['admins']:
                msg.add('%s is already an admin.', target)
            else:
                modconf['admins'].append(target)
                modconf['admins'].sort()
                msg.add('Added %s to the admin list.', target)
    elif action == 'remove':
        if not target.isdigit():
            msg.add("I'm not sure what <code>%s</code> is\u2014it's not an admin!", target)
        else:
            target = int(target)
            if target not in modconf['admins']:
                msg.add("Oops, looks like %s isn't an admin [any more?].", target)
            elif target == ctx.user['id']:
                msg.add("You can't remove yourself from the admin list.")
            else:
                modconf['admins'].remove(target)
                msg.add('Removed %s from the admin list.', target)

    for admin_id in sorted(modconf['admins']):
        if admin_id != ctx.user['id']:
            msg.button('Remove %s' % admin_id, 'remove %s' % admin_id)
    ctx.set_conversation('add')
