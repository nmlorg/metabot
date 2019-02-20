"""Simple group/supergroup moderator tools."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import adminui


def modpredispatch(ctx, unused_msg, modconf):  # pylint: disable=missing-docstring
    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        group_id = '%s' % ctx.chat['id']
        groupconf = modconf[group_id]
        groupconf['title'] = ctx.chat.get('title')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type == 'join':
        return join(ctx, msg, modconf)

    return False


def join(ctx, msg, modconf):
    """Respond to new users joining a group chat."""

    greeting = modconf['%s' % ctx.chat['id']].get('greeting')
    if greeting:
        for user in ctx.data:
            if not user['is_bot']:
                if ('pinned message' in greeting and ctx.groupinfo.data.username and
                        ctx.groupinfo.data.pinned_message_id):
                    link = '<a href="https://t.me/%s/%s">pinned message</a>' % (
                        ctx.groupinfo.data.username, ctx.groupinfo.data.pinned_message_id)
                    greeting = greeting.replace('pinned message', link)
                msg.quiet = True
                return msg.add(greeting)


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
    fields = (
        ('calendars', adminui.calendars, 'Which calendars should be listed in /events?'),
        ('daily', adminui.integer,
         'Should I announce upcoming events once a day? If so, at what hour?'),
        ('dailytext', adminui.freeform,
         'One or more messages (one per line) to use/cycle through for the daily announcement.'),
        ('greeting', adminui.freeform, 'How should I greet people when they join?'),
        ('maxeventscount', adminui.integer, 'How many events should be listed in /events?'),
        ('maxeventsdays', adminui.integer, 'How many days into the future should /events look?'),
        ('timezone', adminui.timezone, 'What time zone should be used in /events?'),
    )
    return adminui.fields(ctx, msg, groupconf, fields, field, text)
