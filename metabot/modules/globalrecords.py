"""Record global group and user info."""

from __future__ import absolute_import, division, print_function, unicode_literals


def modpredispatch(ctx, unused_msg, unused_modconf):  # pylint: disable=missing-docstring
    conf = ctx.bot.multibot.conf

    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        conf['groups'][ctx.chat['id']] = {k: v for k, v in ctx.chat.items() if k != 'id'}

    if ctx.user:
        userinfo = {k: v for k, v in ctx.user.items() if k != 'id'}
        first_name = userinfo.get('first_name')
        last_name = userinfo.get('last_name', '')
        if first_name and last_name:
            userinfo['name'] = '%s %s' % (first_name, last_name)
        elif first_name:
            userinfo['name'] = first_name
        else:
            userinfo['name'] = last_name
        conf['users'][ctx.user['id']] = userinfo
