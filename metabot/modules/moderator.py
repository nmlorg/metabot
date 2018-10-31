"""Simple group/supergroup moderator tools."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import adminui


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
    if ctx.type == 'pin':
        return pin(ctx, msg, modconf)

    return False


def join(ctx, msg, modconf):
    """Respond to new users joining a group chat."""

    groupconf = modconf['%s' % ctx.chat['id']]
    greeting = groupconf.get('greeting')
    if greeting:
        for user in ctx.data:
            if not user['is_bot']:
                if ('pinned message' in greeting and groupconf.get('username') and
                        groupconf.get('pinned_message_id')):
                    link = '<a href="https://t.me/%s/%s">pinned message</a>' % (
                        groupconf['username'], groupconf['pinned_message_id'])
                    greeting = greeting.replace('pinned message', link)
                msg.quiet = True
                return msg.add(greeting)


def pin(ctx, unused_msg, modconf):
    """Record the message id when a group's pinned message changes."""

    groupconf = modconf['%s' % ctx.chat['id']]
    groupconf['pinned_message_id'] = ctx.data['message_id']


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
    fields = {'calendars', 'greeting', 'maxeventscount', 'maxeventsdays', 'timezone'}
    return adminui.fields(ctx, msg, groupconf, fields, field, text)
