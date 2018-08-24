"""Simple group/supergroup moderator tools."""

from __future__ import absolute_import, division, print_function, unicode_literals


def dispatch(ctx):  # pylint: disable=missing-docstring
    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        group_id = str(ctx.chat['id'])
        modconf = ctx.bot.get_modconf('moderator')
        groupconf = modconf.get(group_id)
        if groupconf is None:
            groupconf = modconf[group_id] = {}
        groupconf['title'] = ctx.chat.get('title')
        groupconf['type'] = ctx.chat.get('type')
        groupconf['username'] = ctx.chat.get('username')

    if ctx.type == 'join':
        return join(ctx)

    return False


def join(ctx):
    """Respond to new users joining a group chat."""

    modconf = ctx.bot.get_modconf('moderator')
    groupconf = modconf.get(str(ctx.chat['id'])) or {}
    if groupconf.get('greeting') and not ctx.user.get('is_bot'):
        return ctx.reply_html(groupconf['greeting'])


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTUSER moderator."""

    group_id, _, field = ctx.text.partition(' ')
    field, _, text = field.lstrip().partition(' ')

    if group_id not in modconf:
        msg.action = 'Choose a group'
        for group_id, groupconf in sorted(modconf.items()):
            msg.button('%s (%s)' % (group_id, groupconf['title']),
                       '/%s %s' % (ctx.command, group_id))
        msg.button('Back', '/' + ctx.command.rsplit(None, 1)[0])
        return msg.reply(ctx)

    fields = {'greeting'}

    if field not in fields:
        if field:
            msg.add("I can't set <code>%s</code>.", field)
    elif text:
        if text.lower() in ('-', 'none', 'off'):
            text = ''
        if modconf[group_id].get(field):
            if text:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.', field,
                        modconf[group_id][field], text)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', field,
                        modconf[group_id][field])
        elif text:
            msg.add('Set <code>%s</code> to <code>%s</code>.', field, text)
        else:
            msg.add('Unset <code>%s</code>.', field)
        if text:
            modconf[group_id][field] = text
        else:
            modconf[group_id].pop(field, None)
        ctx.bot.multibot.save()
    else:
        msg.action = 'Type a new value for ' + field
        if modconf[group_id].get(field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', field,
                    modconf[group_id][field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')
        msg.button('Back', '/%s %s' % (ctx.command, group_id))
        ctx.set_conversation('%s %s' % (group_id, field))
        return msg.reply(ctx)

    msg.action = 'Choose a field'
    for field in sorted(fields):
        msg.button(field, '/%s %s %s' % (ctx.command, group_id, field))
    msg.button('Back', '/' + ctx.command)
    return msg.reply(ctx)