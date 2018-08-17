"""Manage the admin list."""

from __future__ import absolute_import, division, print_function, unicode_literals


def _validate(ctx):
    """Verify the user is in the target bot's admin list."""

    mod_config = ctx.bot.config['modules']['admin']

    if ctx.user['id'] in mod_config['admins']:
        return True

    ctx.reply_html(
        "Hi! You aren't one of my admins. If you should be, ask a current admin to add you by "
        'opening a chat with me (@%s) and typing:\n'
        '\n'
        '<pre>/%s admins add %s</pre>', ctx.bot.config['username'], ctx.command, ctx.user['id'])


def default(ctx):  # pylint: disable=missing-docstring
    if not _validate(ctx):
        return

    message = [
        'Bot Admin: <b>Select a command</b>',
        '',
    ]
    keyboard = [
        [{
            'text': 'Admin List',
            'callback_data': '/%s admins' % ctx.command,
        }],
    ]
    ctx.reply_html('\n'.join(message), reply_markup={'inline_keyboard': keyboard})


def admins(ctx):  # pylint: disable=missing-docstring,too-many-branches
    if not _validate(ctx):
        return

    mod_config = ctx.bot.config['modules']['admin']

    command = ctx.text.partition(' ')[2]
    command, _, target = command.partition(' ')

    message = [
        'Bot Admin \u203a Admin List: <b>Choose an admin</b>',
        '',
        ('Type the user id (a number like <code>431603199</code>) of the user to add as an admin, '
         'or select an existing admin to remove.'),
        '',
    ]

    if command == 'add':
        if not target.isdigit():
            message.append("I'm not sure what <code>%s</code> is--it's not a user id!" % target)
        else:
            target = int(target)
            if target in mod_config['admins']:
                message.append('%s is already an admin.' % target)
            else:
                mod_config['admins'].append(target)
                mod_config['admins'].sort()
                ctx.bot.multibot.save()
                message.append('Added %s to the admin list.' % target)
    elif command == 'remove':
        if not target.isdigit():
            message.append("I'm not sure what <code>%s</code> is--it's not an admin!" % target)
        else:
            target = int(target)
            if target not in mod_config['admins']:
                message.append("Oops, looks like %s isn't an admin [any more?]." % target)
            elif target == ctx.user['id']:
                message.append("You can't remove yourself from the admin list.")
            else:
                mod_config['admins'].remove(target)
                ctx.bot.multibot.save()
                message.append('Removed %s from the admin list.' % target)

    keyboard = []
    for admin in sorted(mod_config['admins']):
        if admin != ctx.user['id']:
            keyboard.append([{
                'text': 'Remove %s' % admin,
                'callback_data': '/%s admins remove %s' % (ctx.command, admin),
            }])
    keyboard.append([{'text': 'Back', 'callback_data': '/' + ctx.command}])
    ctx.set_conversation('admins add')
    ctx.reply_html('\n'.join(message), reply_markup={'inline_keyboard': keyboard})
