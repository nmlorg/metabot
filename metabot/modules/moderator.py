"""Simple group/supergroup moderator tools."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot import util


def modpredispatch(ctx, unused_msg, modconf):  # pylint: disable=missing-docstring
    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        group_id = '%s' % ctx.chat['id']
        groupconf = modconf[group_id]
        groupconf['title'] = ctx.chat.get('title')
        groupconf['type'] = ctx.chat.get('type')
        groupconf['username'] = ctx.chat.get('username')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type == 'join':
        return join(ctx, msg, modconf)

    return False


def join(ctx, msg, modconf):
    """Respond to new users joining a group chat."""

    groupconf = modconf['%s' % ctx.chat['id']]
    if groupconf.get('greeting') and not ctx.user.get('is_bot'):
        msg.add(groupconf['greeting'])


def admin(ctx, msg, modconf):  # pylint: disable=too-many-branches
    """Handle /admin BOTNAME moderator."""

    group_id, field, text = ctx.split(3)

    if group_id not in modconf:
        msg.action = 'Choose a group'
        for group_id, groupconf in sorted(modconf.items()):
            msg.button('%s (%s)' % (group_id, groupconf['title']), group_id)
        return

    msg.path(group_id)
    groupconf = modconf[group_id]

    if field == 'calendars':
        msg.path(field)
        return util.adminui.calendars(ctx, msg, groupconf, 'calendars', text)
    if field == 'timezone':
        msg.path(field)
        return util.adminui.timezone(ctx, msg, groupconf, 'timezone', text)

    fields = {'calendars', 'greeting', 'timezone'}

    if field not in fields:
        if field:
            msg.add("I can't set <code>%s</code>.", field)
    elif text:
        if text.lower() in ('-', 'none', 'off'):
            text = ''
        if groupconf.get(field):
            if text:
                msg.add('Changed <code>%s</code> from <code>%s</code> to <code>%s</code>.', field,
                        groupconf[field], text)
            else:
                msg.add('Unset <code>%s</code> (was <code>%s</code>).', field, groupconf[field])
        elif text:
            msg.add('Set <code>%s</code> to <code>%s</code>.', field, text)
        else:
            msg.add('Unset <code>%s</code>.', field)
        if text:
            groupconf[field] = text
        else:
            groupconf.pop(field)
    else:
        msg.path(field)
        msg.action = 'Type a new value for ' + field
        if groupconf.get(field):
            msg.add('<code>%s</code> is currently <code>%s</code>.', field, groupconf[field])
        msg.add('Type your new value, or type "off" to disable/reset to default.')
        return ctx.set_conversation('%s %s' % (group_id, field))

    msg.action = 'Choose a field'
    for field in sorted(fields):
        msg.button(field, field)
