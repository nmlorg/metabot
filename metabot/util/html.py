"""Telegram-specific HTML sanitizer."""

import html
import html.parser
import logging


def cgi_escape(text):  # pylint: disable=missing-docstring
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                   '&gt;').replace('"', '&quot;')


class _HTMLSanitizer(html.parser.HTMLParser):
    __pieces = __strip = __stack = None

    def sanitize(self, text, strip=False):
        """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

        self.__pieces = []
        self.__strip = strip
        self.__stack = []
        self.feed(text)
        self.close()
        self.handle_endtag(None)
        return ''.join(self.__pieces)

    naked = {'b', 'del', 'em', 'i', 'ins', 'pre', 's', 'strike', 'strong', 'tg-spoiler', 'u'}
    coupled = {
        'a': 'href',
        'blockquote': 'expandable',
        'code': 'class',
        'span': 'class',
        'tg-emoji': 'emoji-id',
    }

    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'div', 'p'):
            self.__pieces.append('\n')
            return
        if self.__strip or tag not in self.naked and tag not in self.coupled:
            return
        self.__stack.append(tag)
        if tag in self.coupled:
            attr = self.coupled[tag]
            attrs = dict(attrs)
            if attrs.get(attr):
                value = cgi_escape(attrs[attr])
                self.__pieces.append(f'<{tag} {attr}="{value}">')
            elif attr in attrs:
                self.__pieces.append(f'<{tag} {attr}>')
            else:
                self.__pieces.append(f'<{tag}>')
        else:
            self.__pieces.append(f'<{tag}>')

    def handle_endtag(self, tag):
        while self.__stack:
            lasttag = self.__stack.pop()
            self.__pieces.append(f'</{lasttag}>')
            if lasttag == tag:
                break

    def handle_data(self, data):
        self.__pieces.append(cgi_escape(data))

    def handle_entityref(self, name):  # pragma: no cover
        if name in ('lt', 'gt', 'amp', 'quot'):
            self.__pieces.append(f'&{name};')
        else:
            codepoint = html.entities.name2codepoint.get(name)
            if codepoint:
                self.__pieces.append(chr(codepoint))
            else:
                self.__pieces.append(f'&amp;{name};')

    def handle_charref(self, name):  # pragma: no cover
        name = name.lower()
        try:
            if name.startswith('x'):
                codepoint = int(name[1:], 16)
            else:
                codepoint = int(name)
            self.__pieces.append(cgi_escape(chr(codepoint)))
        except (OverflowError, ValueError):
            self.__pieces.append(f'&amp;#{name};')

    def error(self, message):  # pragma: no cover  pylint: disable=missing-function-docstring
        # Remove when support for Python below 3.10 is dropped.
        logging.error('HTML sanitizer error: %s', message)


def sanitize(text, strip=False):
    """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

    return _HTMLSanitizer().sanitize(text, strip=strip)
