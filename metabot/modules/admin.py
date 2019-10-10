"""Manage the admin list."""

import uuid

from metabot.util import adminui

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
        if ctx.command == 'whoami':
            return whoami(ctx, msg)
        if ctx.command == '_bootstrap':
            return bootstrap(ctx, msg, modconf)

    return False


def default(ctx, msg):  # pylint: disable=missing-docstring
    ctx.private = True
    msg.path('/admin', 'Bot Admin')
    frame = adminui.Frame(ctx, msg, ctx.bot.multibot.conf, 'bots', None, ctx.text)
    menu = adminui.Menu()
    for username, botconf in frame.value.items():
        if ctx.user['id'] in botconf['issue37']['admin']['admins']:
            menu.add(username)

    if not menu.fields:
        return msg.add(
            "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by "
            'opening a chat with me (@%s) and typing:\n'
            '\n'
            '<pre>/admin %s admin add %s</pre>', ctx.bot.username, ctx.bot.username, ctx.user['id'])

    frame, handler = menu.select(frame)
    if not handler:
        msg.add('This is a metabot! Check out https://github.com/nmlorg/metabot/issues to keep '
                'track of bugs and features.')
        try:
            msg.add(open('config/admin_motd').read().strip())
        except IOError:
            pass
        msg.add('To configure your bot, choose its username:')
        return menu.display(frame, what='bot')

    msg.path(frame.field)
    ctx.targetbotuser = frame.field
    ctx.targetbotconf = frame.value

    menu = adminui.Menu()
    for modname, module in ctx.bot.multibot.modules.items():
        if hasattr(module, 'admin'):
            menu.add(modname, module.admin, module.__doc__.splitlines()[0].rstrip('.'))

    if not menu.fields:  # pragma: no cover
        return msg.add(
            "Hi! There aren't any configurable modules installed. Contact a metabot admin to "
            'install one.')

    menu.handle(frame, what='module')


def whoami(ctx, msg):
    """Simply tell the user their userid (primarily to copy/paste into /admin BOTNAME admin)."""

    msg.add('<code>%s</code>', ctx.user['id'])


def bootstrap(ctx, msg, modconf):
    """Add the user who sent the command to the current bot's admin list."""

    if ctx.text == BOOTSTRAP_TOKEN and not modconf['admins']:
        modconf['admins'] = [ctx.user['id']]
        msg.add('Added %s to the admin list.', ctx.user['id'])


def admin(frame):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME admin (configure the admin module itself)."""

    ctx, msg, modconf = frame.ctx, frame.msg, frame.value
    if 'admins' not in modconf:  # pragma: no cover
        modconf['admins'] = []

    target = None
    if ctx.forward_from:
        target = ctx.forward_from
    elif frame.text.isdigit():
        target = int(frame.text)
    elif ctx.forwarded:
        msg.add(
            "I can't tell exactly who sent that message, possibly because the sender enabled <a "
            'href="https://telegram.org/blog/unsend-privacy-emoji#anonymous-forwarding">Anonymous '
            'Forwarding</a>. You can either ask them to temporarily re-enable normal forwarding, '
            'or ask them to open a chat with me, type <code>/whoami</code>, then forward or '
            'copy/paste the number they receive to you (to copy/paste on to me).')
    elif frame.text:
        msg.add("I'm not sure what <code>%s</code> is\u2014it's not a user id!", frame.text)

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
