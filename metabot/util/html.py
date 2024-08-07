"""Telegram-specific HTML sanitizer."""

import html
import html.parser
import logging


def escape(text):  # pylint: disable=missing-docstring
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                   '&gt;').replace('"', '&quot;')


class _HTMLSanitizer(html.parser.HTMLParser):
    __pieces = __strip = __remaining = __stack = None

    def sanitize(self, text, strip=False, length=None):
        """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

        self.__pieces = []
        self.__strip = strip
        self.__remaining = length
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
        if self.__remaining is not None and not self.__remaining:
            return
        if tag in ('br', 'div', 'p'):
            self.__append('\n')
            return
        if self.__strip or tag not in self.naked and tag not in self.coupled:
            return
        self.__stack.append(tag)
        if tag in self.coupled:
            attr = self.coupled[tag]
            attrs = dict(attrs)
            if attrs.get(attr):
                value = escape(attrs[attr])
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

    def __append(self, data):
        if self.__remaining is None:
            return self.__pieces.append(data)

        if len(data) <= self.__remaining and '&' not in data:
            self.__remaining -= len(data)
            return self.__pieces.append(data)

        inentity = False
        for char in data:
            if not self.__remaining:
                break
            self.__pieces.append(char)
            if inentity:
                if char == ';':
                    self.__remaining -= 1
                    inentity = False
            else:
                if char == '&':
                    inentity = True
                else:
                    self.__remaining -= 1

    def handle_data(self, data):
        self.__append(escape(data))

    def error(self, message):  # pragma: no cover  pylint: disable=missing-function-docstring
        # Remove when support for Python below 3.10 is dropped.
        logging.error('HTML sanitizer error: %s', message)


def sanitize(text, strip=False):
    """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

    return _HTMLSanitizer().sanitize(text, strip=strip)


def truncate(text, length):
    """Truncate text to at most length non-markup characters."""

    return _HTMLSanitizer().sanitize(text, length=length)
