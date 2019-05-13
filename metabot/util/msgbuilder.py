"""Quick template for metabot's custom message style."""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    unicode
except NameError:
    unicode = str  # pylint: disable=invalid-name,redefined-builtin


def cgi_escape(text):  # pylint: disable=missing-docstring
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                   '&gt;').replace('"', '&quot;')


class MessageBuilder(object):
    """Quick template for metabot's custom message style."""

    action = None
    quiet = False

    def __init__(self):
        self._path = []
        self._title = []
        self._lines = []
        self._keyboard = []

    def __bool__(self):
        return bool(self._title or self._lines)

    __nonzero__ = __bool__

    def path(self, path, title=None):
        """Add path to the visible title and to the path used to calculate button callbacks."""

        self._path.append(path)
        self._title.append(title or path)

    def add(self, line, *args):
        """Add line to the message body, interpolating HTML-escaped args if provided."""

        if args:
            line %= tuple(cgi_escape(unicode(arg)) for arg in args)
        self._lines.append(line)

    def _make_button(self, data):
        if data:
            text, callback_data = data
        else:
            text = '\xa0'
            callback_data = '/stop'
        path = self._path[:]
        while path and callback_data.startswith('..'):
            path.pop()
            callback_data = callback_data[len('..'):].lstrip()
        if not callback_data.startswith('/'):
            if callback_data:
                path.append(callback_data)
            callback_data = ' '.join(path)
        return {'text': cgi_escape(text), 'callback_data': callback_data}

    def button(self, text, callback_data):
        """Add a row to the keyboard with single callback button."""

        self.buttons([(text, callback_data)])

    def buttons(self, buttons):
        """Add a row to the keyboard with one or more callback buttons."""

        self._keyboard.append(buttons)

    def reply(self, ctx):
        """Build the message and pipe it through ctx.reply_html."""

        first_line = cgi_escape(' \u203a '.join(self._title))
        if first_line and self.action:
            first_line += ': '
        if self.action:
            first_line = '%s<b>%s</b>' % (first_line, cgi_escape(self.action))
        lines = first_line and [first_line] + self._lines or self._lines
        if len(self._path) > 1:
            self.button('Back', '..')
        kwargs = {}
        if self._keyboard:
            keyboard = [[self._make_button(data) for data in row] for row in self._keyboard]
            kwargs['reply_markup'] = {'inline_keyboard': keyboard}
        if self.quiet:
            kwargs['disable_notification'] = True
        ctx.set_conversation(' '.join(self._path))
        return ctx.reply_html('\n\n'.join(lines), disable_web_page_preview=True, **kwargs)
