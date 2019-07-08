"""Create custom commands that just return fixed messages."""

from metabot.util import adminui


def modhelp(unused_ctx, modconf, sections):  # pylint: disable=missing-docstring
    for command, data in modconf.items():
        if not data.get('text'):
            continue
        message = data['text'].replace('\n', ' ')
        if len(message) > 30:
            message = message[:29] + '\u2026'
        sections['commands'].add('/%s \u2013 "%s"' % (command, message))


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


def admin(ctx, msg, frame):
    """Handle /admin BOTNAME echo."""

    modconf = frame.value
    command, _, text = frame.text.partition(' ')
    command = command.lower()

    if not command:
        msg.action = 'Choose a command'
        msg.add(
            "Type the name of a command to add (like <code>rules</code>\u2014don't include a slash "
            'at the beginning!), or select an existing echo.')
        for command, data in sorted(modconf.items()):
            title = '/' + command
            if data.get('text'):
                title = '%s (%s)' % (title, data['text'].replace('\n', ' '))
            msg.button(title, command)
        return

    msg.path(command)

    fields = (
        ('text', adminui.freeform,
         'The message, sticker, or image to send in response to /%s.' % command),
        ('paginate', adminui.bool, 'For multiline messages, display just one line at a time?'),
        ('private', adminui.bool, 'Send the message in group chats, or just in private?'),
    )
    return adminui.fields(ctx, msg, adminui.Frame(modconf, command, None, text), fields)
