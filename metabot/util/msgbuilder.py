"""Quick template for metabot's custom message style."""

from __future__ import absolute_import, division, print_function, unicode_literals

import cgi


def cgi_escape(string):  # pylint: disable=missing-docstring
    return cgi.escape(string, True)  # pylint: disable=deprecated-method


class MessageBuilder(object):
    """Quick template for metabot's custom message style."""

    action = None

    def __init__(self):
        self._path = []
        self._title = []
        self._lines = []
        self._keyboard = []

    def path(self, path, title=None):
        """Add path to the visible title and to the path used to calculate button callbacks."""

        self._path.append(path)
        self._title.append(title or path)

    def add(self, line, *args):
        """Add line to the message body, interpolating HTML-escaped args if provided."""

        if args:
            line %= tuple(cgi_escape(str(arg)) for arg in args)
        self._lines.append(line)

    def button(self, text, callback_data):
        """Add a row to the keyboard with single callback button."""

        path = self._path[:]
        while path and callback_data.startswith('..'):
            path.pop()
            callback_data = callback_data[len('..'):].lstrip()
        if not callback_data.startswith('/'):
            if callback_data:
                path.append(callback_data)
            callback_data = ' '.join(path)
        self._keyboard.append([{'text': cgi_escape(text), 'callback_data': callback_data}])

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
        return ctx.reply_html(
            '\n\n'.join(lines),
            reply_markup={'inline_keyboard': self._keyboard},
            disable_web_page_preview=True)
