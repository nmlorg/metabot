"""Record global group and user info."""

from __future__ import absolute_import, division, print_function, unicode_literals


def modpredispatch(ctx, unused_msg, unused_modconf):  # pylint: disable=missing-docstring
    conf = ctx.bot.multibot.conf

    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        groupinfo = conf['groups'][ctx.chat['id']]
        for k, val in ctx.chat.items():
            if k != 'id':
                groupinfo[k] = val

        if ctx.type == 'pin':
            groupinfo['pinned_message_id'] = ctx.data['message_id']

    if ctx.user:
        userinfo = conf['users'][ctx.user['id']]
        for k, val in ctx.user.items():
            if k != 'id':
                userinfo[k] = val
        userinfo['name'] = (
            '%s %s' % (ctx.user.get('first_name', ''), ctx.user.get('last_name', ''))).strip()
