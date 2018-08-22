"""Manage the admin list."""

from __future__ import absolute_import, division, print_function, unicode_literals


def dispatch(ctx):
    """Verify the user is in the target bot's admin list and dispatch relevant contexts."""

    callback = {
        'admin': default,
        'admin_admins': admins,
    }.get(ctx.command)
    if not callback:
        return False

    ctx.mod_config = ctx.bot.get_modconf('admin')
    if 'admins' not in ctx.mod_config:
        ctx.mod_config['admins'] = []

    if ctx.user['id'] not in ctx.mod_config['admins']:
        return ctx.reply_html(
            "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by "
            'opening a chat with me (@%s) and typing:\n'
            '\n'
            '<pre>/admin_admins add %s</pre>', ctx.bot.username, ctx.user['id'])

    return callback(ctx)


def default(ctx):  # pylint: disable=missing-docstring
    message = [
        'Bot Admin: <b>Select a command</b>',
        '',
    ]
    keyboard = [
        [{
            'text': 'Admin List',
            'callback_data': '/admin_admins',
        }],
    ]
    ctx.reply_html('\n'.join(message), reply_markup={'inline_keyboard': keyboard})


def admins(ctx):  # pylint: disable=missing-docstring,too-many-branches
    action, _, target = ctx.text.partition(' ')

    message = [
        'Bot Admin \u203a Admin List: <b>Choose an admin</b>',
        '',
        ('Type the user id (a number like <code>431603199</code>) of the user to add as an admin, '
         'or select an existing admin to remove.'),
        '',
    ]

    if action == 'add':
        if not target.isdigit():
            message.append("I'm not sure what <code>%s</code> is--it's not a user id!" % target)
        else:
            target = int(target)
            if target in ctx.mod_config['admins']:
                message.append('%s is already an admin.' % target)
            else:
                ctx.mod_config['admins'].append(target)
                ctx.mod_config['admins'].sort()
                ctx.bot.multibot.save()
                message.append('Added %s to the admin list.' % target)
    elif action == 'remove':
        if not target.isdigit():
            message.append("I'm not sure what <code>%s</code> is--it's not an admin!" % target)
        else:
            target = int(target)
            if target not in ctx.mod_config['admins']:
                message.append("Oops, looks like %s isn't an admin [any more?]." % target)
            elif target == ctx.user['id']:
                message.append("You can't remove yourself from the admin list.")
            else:
                ctx.mod_config['admins'].remove(target)
                ctx.bot.multibot.save()
                message.append('Removed %s from the admin list.' % target)

    keyboard = []
    for admin in sorted(ctx.mod_config['admins']):
        if admin != ctx.user['id']:
            keyboard.append([{
                'text': 'Remove %s' % admin,
                'callback_data': '/admin_admins remove %s' % admin,
            }])
    keyboard.append([{'text': 'Back', 'callback_data': '/admin'}])
    ctx.set_conversation('add')
    ctx.reply_html('\n'.join(message), reply_markup={'inline_keyboard': keyboard})
