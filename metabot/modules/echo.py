"""Create custom commands that just return fixed messages."""

from metabot.util import adminui
from metabot.util import html


def modhelp(*, ctx, sections):  # pylint: disable=missing-docstring
    for command, data in ctx.mgr.bot_conf['echo'].items():
        if not data.get('text') or data.get('hidden'):
            continue
        message = data['text']
        if (message.startswith('document:') or message.startswith('photo:') or
                message.startswith('sticker:')):
            message = message.split(None, 1)
            if len(message) == 2:
                message = message[1]
            else:
                message = message[0].split(':', 1)[0]
            section = 'media'
        else:
            section = 'text'

        message = html.sanitize(message, strip=True).replace('\n', ' ')
        if len(message) > 30:
            message = message[:29] + '\u2026'
        sections[section].add(f'/{command} \u2013 {message}')


def moddispatch(ctx, msg, modconf):  # pylint: disable=missing-docstring
    if (ctx.type in ('message', 'callback_query') and ctx.command in modconf and
            modconf[ctx.command].get('text')):
        return echo(ctx, msg, modconf[ctx.command])

    return False


def echo(ctx, msg, data):  # pylint: disable=missing-docstring
    ctx.private = data.get('private')
    if not data.get('paginate'):
        msg.add(data['text'])
    else:
        lines = [line for line in data['text'].splitlines() if line.strip()]
        page = ctx.text.isdigit() and int(ctx.text) or 1
        for line in lines[:page]:
            msg.add('%s', line)
        if page < len(lines):
            msg.button('More (%i/%i)' % (page, len(lines)), '/%s %i' % (ctx.command, page + 1))


def admin(frame):
    """Handle /admin BOTNAME echo."""

    msg = frame.msg
    menu = adminui.Menu()
    for command, data in frame.value.items():
        menu.add(command, desc=data.get('text', '').replace('\n', ' '))
    menu.add(None)
    frame, handler = menu.select(frame)
    if not handler:
        msg.action = 'Choose a command'
        msg.add(
            "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash "
            'at the beginning!), or select an existing echo.')
        return menu.display(frame, what='command')

    msg.path(frame.field)

    adminui.Menu(
        ('text', adminui.freeform,
         'The message, sticker, or image to send in response to /%s.' % frame.field),
        ('hidden', adminui.bool, 'Hide from /help?'),
        ('paginate', adminui.bool, 'For multiline messages, display just one line at a time?'),
        ('private', adminui.bool, 'Send the message in group chats, or just in private?'),
    ).handle(frame)
