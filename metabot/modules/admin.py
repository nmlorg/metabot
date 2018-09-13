"""Manage the bot's state and settings."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot import util


def modhelp(ctx, unused_modconf, sections):  # pylint: disable=missing-docstring
    bots = sorted(username for username, botconf in ctx.bot.multibot.bots.items()
                  if ctx.user['id'] in botconf['admin']['admins'])

    if bots:
        sections['commands'].add("/admin \u2013 Manage the bot's state and settings")


def dispatch(ctx):  # pylint: disable=missing-docstring
    if ctx.type in ('message', 'callback_query') and ctx.command == 'admin':
        ctx.private = True
        return default(ctx)

    return False


def default(ctx):  # pylint: disable=missing-docstring
    bots = sorted(username for username, botconf in ctx.bot.multibot.bots.items()
                  if ctx.user['id'] in botconf['admin']['admins'])

    if not bots:
        return ctx.reply_html(
            "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by "
            'opening a chat with me (@%s) and typing:\n'
            '\n'
            '<pre>/admin %s admin add %s</pre>', ctx.bot.username, ctx.bot.username, ctx.user['id'])

    msg = util.msgbuilder.MessageBuilder()
    msg.path('/admin', 'Bot Admin')

    username, _, text = ctx.text.partition(' ')
    #if not username and len(bots) == 1:
    #    username = bots[0]

    if username not in bots:
        msg.action = 'Choose a bot'
        for username in bots:
            msg.button(username, '/admin ' + username)
        return msg.reply(ctx)

    msg.path(username)

    modules = {
        modname: module
        for modname, module in ctx.bot.multibot.modules.items()
        if hasattr(module, 'admin')
    }

    if not modules:
        return ctx.reply_html(
            "Hi! There aren't any configurable modules installed. Contact a metabot admin to "
            'install one.')

    modname, _, text = text.lstrip().partition(' ')
    #if not modname and len(modules) == 1:
    #    modname = list(modules)[0]

    if modname not in modules:
        msg.action = 'Choose a module'
        for modname, module in sorted(modules.items()):
            label = modname
            if getattr(module, '__doc__', None):
                label = '%s \u2022 %s' % (label, module.__doc__.splitlines()[0].rstrip('.'))
            msg.button(label, '/admin %s %s' % (username, modname))
        return msg.reply(ctx)

    msg.path(modname)

    admin_callback = modules[modname].admin
    ctx.command = 'admin %s %s' % (username, modname)
    ctx.text = text.lstrip()
    return admin_callback(ctx, msg, ctx.bot.multibot.bots[username][modname])


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME admin (configure the admin module itself)."""

    action, _, target = ctx.text.partition(' ')

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
    return msg.reply(ctx)
