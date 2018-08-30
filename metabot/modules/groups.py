"""Display group chats."""

from __future__ import absolute_import, division, print_function, unicode_literals

import cgi
import collections
import hashlib
import json
import re

import ntelebot
import requests

from metabot import util

try:
    import html
except ImportError:  # pragma: no cover
    import HTMLParser

    html_unescape = HTMLParser.HTMLParser().unescape  # pylint: disable=invalid-name
else:
    html_unescape = html.unescape  # pylint: disable=invalid-name


def cgi_escape(string):  # pylint: disable=missing-docstring
    return cgi.escape(string, True)  # pylint: disable=deprecated-method


ALIASES = ('channel', 'group', 'room')


def dispatch(ctx):  # pylint: disable=missing-docstring
    if (ctx.type in ('message', 'callback_query') and ctx.command and
            ctx.command.rstrip('s') in ALIASES):
        return default(ctx)

    if ctx.type == 'inline_query' and ctx.prefix.lstrip('/').rstrip('s') in ALIASES:
        return inline(ctx)

    return False


def default(ctx):
    """Handle /groups."""

    ctx.private = True

    msg = util.msgbuilder.MessageBuilder()
    msg.path('/groups', 'Group List')

    groups_by_location = collections.defaultdict(list)
    for group in ctx.bot.get_modconf('groups')['groups'].values():
        if group['invite_link'] or group['username']:
            groups_by_location[group['location'] or 'Worldwide'].append(group)

    if not groups_by_location:
        msg.add("I don't know about any public groups yet, sorry!")
        return msg.reply(ctx)

    location = ctx.text
    if location not in groups_by_location:
        msg.action = 'Choose a location'
        for location in sorted(groups_by_location, key=lambda name: tuple(reversed(name.split()))):
            msg.button(location, '/groups ' + location)
        return msg.reply(ctx)

    msg.path(location)

    for group in sorted(groups_by_location[location], key=lambda group: group['name']):
        invite_link = group['invite_link'] or 'https://t.me/' + group['username']
        message = '<a href="%s">%s</a>' % (invite_link, cgi_escape(group['name']))
        if group['desc']:
            message = '%s\n%s' % (message,
                                  re.sub('\\s*\n\\s*', ' \u2022 ', cgi_escape(group['desc'])))
        msg.add(message)

    return msg.reply(ctx)


def inline(ctx):
    """Handle @BOTNAME groups."""

    terms = ctx.text.lower().split()[1:]
    results = []
    for group in sorted(
            ctx.bot.get_modconf('groups')['groups'].values(), key=lambda group: group['name']):
        if len(results) >= 25:
            break
        if group['invite_link'] or group['username']:
            for term in terms:
                if term not in group['name'].lower() and term not in group['desc'].lower():
                    break
            else:
                invite_link = group['invite_link'] or 'https://t.me/' + group['username']
                message = '<a href="%s">%s</a>' % (invite_link, cgi_escape(group['name']))
                if group['desc']:
                    message = '%s\n%s' % (message, group['desc'])
                    title = '%s \u2022 %s' % (group['name'], group['username'] or
                                              group['invite_link'])
                    desc = group['desc']
                else:
                    title = group['name']
                    desc = invite_link
                results.append({
                    'type': 'article',
                    'id': invite_link,
                    'title': title,
                    'input_message_content': {
                        'message_text': message,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': True,
                    },
                    'description': desc,
                })
    ctx.reply_inline(results, cache_time=60)


def admin(ctx, msg, modconf):
    """Handle /admin BOTNAME groups."""

    action, _, text = ctx.text.partition(' ')

    if action == 'add' and text:
        newgroup = get_group(ctx.bot, text)
        if not newgroup:
            msg.add(
                "I'm not sure what <code>%s</code> is! If it's a public group, it should have a "
                '<code>@USERNAME</code> code or <code>https://t.me/USERNAME</code> link in the '
                "group description screen. If it's a private group, and you are an admin, there "
                'should be a <code>https://t.me/joinchat/INVITECODE</code> link in the group '
                "description screen, otherwise you'll need to dig around or ask someone for it. "
                'Once you find it, paste it here:', text)
        else:
            for key, group in modconf['groups'].items():
                if (group['username'] and newgroup['username'] == group['username'] or
                        group['invite_link'] and newgroup['invite_link'] == group['invite_link']):
                    modconf['groups'][key] = newgroup
                    msg.add('Updated <b>%s</b>.', newgroup['name'])
                    break
            else:
                tmp = hashlib.sha1(json.dumps(newgroup, sort_keys=True).encode('ascii'))
                while tmp.hexdigest()[:6] in modconf['groups']:
                    tmp.update('.')
                modconf['groups'][tmp.hexdigest()[:6]] = newgroup
                msg.add('Added <b>%s</b>.', newgroup['name'])
    elif action == 'remove':
        group = modconf['groups'].pop(text)
        if group:
            msg.add('Removed <b>%s</b>.', group['name'])
        else:
            msg.add('Oops, the groups list changed since you loaded that screen, try again.')

    msg.action = 'Type a group username or invite link'
    msg.add('Type the <code>@USERNAME</code> or <code>https://t.me/joinchat/INVITE_LINK</code> for '
            'the group you want to add, or select an existing group to remove:')
    for key, group in sorted(modconf['groups'].items(), key=lambda ent: ent[1]['name']):
        msg.button('%s \u2022 %s' % (group['name'], group['username'] or group['invite_link']),
                   'remove %s' % key)
    ctx.set_conversation('add')
    return msg.reply(ctx)


def get_group(bot, identifier):
    """Try to convert an @username or invite link to a normalized group info dict."""

    if identifier.startswith('tg://join?invite='):
        invite_link = 'https://t.me/joinchat/' + identifier[len('tg://join?invite='):]
        return get_private_group(invite_link)
    if identifier.startswith('https://t.me/joinchat/'):
        return get_private_group(identifier)
    if identifier.startswith('https://t.me/'):
        username = identifier[len('https://t.me/'):]
        return get_public_group(bot, username)
    return get_public_group(bot, identifier.lstrip('@'))


def get_public_group(bot, username):
    """Try to convert a username to a normalized group info dict."""

    try:
        info = bot.get_chat(chat_id='@' + username)
    except ntelebot.errors.Error:
        return

    group = {
        'admins': [],
        'desc': info.get('description', ''),
        'id': info['id'],
        'invite_link': '',
        'location': '',
        'name': info['title'],
        'type': info['type'],
        'username': info['username'],
    }

    try:
        group['admins'] = sorted(
            member['user']['id'] for member in bot.get_chat_administrators(chat_id='@' + username))
    except ntelebot.errors.Error:
        pass

    return group


def get_private_group(invite_link):
    """Try to convert an invite link to a normalized group info dict."""

    info = fetch_opengraph(invite_link)
    if not info.get('title'):
        return

    return {
        'admins': [],
        'desc': info['description'],
        'id': '',
        'invite_link': invite_link,
        'location': '',
        'name': info['title'],
        'type': '',
        'username': '',
    }


def fetch_opengraph(url):
    """Basic (and fragile) Open Graph object fetcher/decoder."""

    values = {}
    for line in requests.get(url).text.splitlines():
        ret = re.search('<meta property="og:([^"]+)" content="([^"]*)">', line)
        if ret:
            key, value = ret.groups()
            values[html_unescape(key)] = html_unescape(value)
    return values
