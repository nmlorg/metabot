"""Simple group/supergroup moderator tools."""

import logging
import random

import ntelebot

from metabot.util import adminui
from metabot.util import humanize


def modinit(multibot):  # pylint: disable=missing-docstring

    def _queue():
        multibot.loop.queue.puthourly(30 * 60, _hourly, jitter=random.random() * 5)

    def _hourly():
        try:
            checked = set()
            for botconf in multibot.conf['bots'].values():
                # See https://github.com/nmlorg/metabot/issues/26.
                bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
                bot.multibot = multibot
                for groupid in botconf['issue37']['moderator']:
                    groupid = int(groupid)
                    if groupid in checked:
                        continue
                    groupdata = multibot.conf['groups'][groupid]
                    try:
                        data = bot.get_chat_administrators(chat_id=groupid)
                    except ntelebot.errors.Error:
                        continue
                    checked.add(groupid)
                    groupdata['admins'] = sorted(member['user']['id'] for member in data)
            log = multibot.conf.finalize()
            if log:
                for path, (value, orig) in sorted(log.items()):
                    pathstr = '.'.join('%s' % part for part in path)
                    logging.info('[moderator] %s: %r -> %r', pathstr, orig, value)
                multibot.conf.save()
        finally:
            _queue()

    _queue()


def modpredispatch(ctx, unused_msg, modconf):  # pylint: disable=missing-docstring
    if ctx.chat and ctx.chat['type'] in ('channel', 'group', 'supergroup'):
        group_id = '%s' % ctx.chat['id']
        groupconf = modconf[group_id]
        groupconf['title'] = ctx.chat.get('title')

        if ctx.type == 'message':
            for target_group_id, target_groupconf in ctx.bot.config['issue37']['moderator'].items():
                if target_groupconf['forward']['from'] == ctx.chat['id']:
                    ctx.forward(int(target_group_id),
                                disable_notification=not target_groupconf['forward']['notify'])


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if ctx.type == 'join':
        join(ctx, msg, modconf)

    if ctx.type in ('message', 'callback_query') and ctx.command == 'mod':
        msg.path('/mod', 'Group Admin')
        ctx.targetbotconf = ctx.bot.config
        return admin(ctx, msg, modconf, botadmin=False)

    return False


def join(ctx, msg, modconf):
    """Respond to new users joining a group chat."""

    greeting = modconf['%s' % ctx.chat['id']].get('greeting')
    if not greeting:
        return
    users = [user for user in ctx.data if not user['is_bot']]
    if not users:
        return

    if 'pinned message' in greeting and ctx.groupinfo.data.pinned_message_id:
        if ctx.groupinfo.data.username:
            url = 'https://t.me/%s/%s' % (ctx.groupinfo.data.username,
                                          ctx.groupinfo.data.pinned_message_id)
        elif -1002147483647 <= ctx.chat['id'] < -1000000000000:
            # See https://github.com/nmlorg/metabot/issues/43.
            url = 'https://t.me/c/%s/%s' % (-1000000000000 - ctx.chat['id'],
                                            ctx.groupinfo.data.pinned_message_id)
        else:
            url = None  # pragma: no cover
        if url:
            greeting = greeting.replace('pinned message', '<a href="%s">pinned message</a>' % url)

    if 'new users' in greeting:
        names = [
            '<a href="tg://user?id=%s">%s</a>' % (user['id'], user['first_name']) for user in users
        ]
        greeting = greeting.replace('new users', humanize.list(names))

    greeting = greeting.replace('chat title', ctx.groupinfo.data.title)

    msg.quiet = True
    msg.add(greeting)


def admin(ctx, msg, modconf, botadmin=True):
    """Handle /admin BOTNAME moderator."""

    groups = sorted(
        group_id for group_id in modconf
        if botadmin or ctx.user['id'] in ctx.bot.multibot.conf['groups'][int(group_id)]['admins'])

    if not groups:
        if botadmin:
            return msg.add(
                "I'm not in any groups! Add me to an existing group from its details screen.")
        return msg.add(
            "Hi! You aren't an admin in any groups I'm in. If you should be, ask a current admin "
            "to promote you from the group's members list.")

    group_id, text = ctx.split(2)

    if group_id not in groups:
        msg.action = 'Choose a group'
        for group_id in groups:
            groupconf = modconf[group_id]
            msg.button('%s (%s)' % (group_id, groupconf['title']), group_id)
        return

    msg.path(group_id)
    groupconf = modconf[group_id]
    fields = (
        ('calendars', adminui.calendars, 'Which calendars should be listed in /events?'),
        ('daily', adminui.integer,
         'Should I announce upcoming events once a day? If so, at what hour?'),
        ('dailydow', adminui.daysofweek,
         'Which days of the week should I announce upcoming events on?'),
        ('dailytext', adminui.freeform,
         'One or more messages (one per line) to use/cycle through for the daily announcement.'),
        ('forward', adminui.forward, 'Automatically forward messages from one chat to this one.'),
        ('greeting', adminui.freeform, 'How should I greet people when they join?'),
        ('maxeventscount', adminui.integer, 'How many events should be listed in /events?'),
        ('maxeventsdays', adminui.integer, 'How many days into the future should /events look?'),
        ('timezone', adminui.timezone, 'What time zone should be used in /events?'),
    )
    return adminui.fields(ctx, msg, groupconf, fields, text)
