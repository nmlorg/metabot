"""Quick template for metabot's custom message style."""

from __future__ import absolute_import, division, print_function, unicode_literals

import cgi


def cgi_escape(string):  # pylint: disable=missing-docstring
    return cgi.escape(string, True)  # pylint: disable=deprecated-method


class MessageBuilder(object):
    """Quick template for metabot's custom message style."""

    action = None

    def __init__(self):
        self.title = []
        self.lines = []
        self.keyboard = []

    def add(self, line, *args):
        """Add line to the message body, interpolating HTML-escaped args if provided."""

        if args:
            line %= tuple(cgi_escape(str(arg)) for arg in args)
        self.lines.append(line)

    def button(self, text, callback_data):
        """Add a row to the keyboard with single callback button."""

        self.keyboard.append([{'text': cgi_escape(text), 'callback_data': callback_data}])

    def reply(self, ctx):
        """Build the message and pipe it through ctx.reply_html."""

        first_line = cgi_escape(' \u203a '.join(self.title))
        if first_line and self.action:
            first_line += ': '
        if self.action:
            first_line = '%s<b>%s</b>' % (first_line, cgi_escape(self.action))
        lines = first_line and [first_line] + self.lines or self.lines
        return ctx.reply_html(
            '\n\n'.join(lines),
            reply_markup={'inline_keyboard': self.keyboard},
            disable_web_page_preview=True)
