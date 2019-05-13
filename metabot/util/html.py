"""Telegram-specific HTML sanitizer."""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import htmlentitydefs
    import HTMLParser  # pragma: no cover
except ImportError:
    import html.entities as htmlentitydefs
    import html.parser as HTMLParser

try:
    unichr
except NameError:
    unichr = chr  # pylint: disable=invalid-name,redefined-builtin


def cgi_escape(text):  # pylint: disable=missing-docstring
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>',
                                                                   '&gt;').replace('"', '&quot;')


class _HTMLSanitizer(HTMLParser.HTMLParser):
    __pieces = __strip = __current = None

    def sanitize(self, text, strip=False):
        """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

        self.__pieces = []
        self.__strip = strip
        self.feed(text)
        self.close()
        return ''.join(self.__pieces)

    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'div', 'p'):
            self.__pieces.append('\n')
            return
        if self.__strip or tag not in ('a', 'b', 'code', 'em', 'i', 'pre', 'strong'):
            return
        if self.__current:
            self.__pieces.append('</%s>' % self.__current)
        self.__current = tag
        if tag == 'a':
            attrs = dict(attrs)
            if attrs.get('href'):
                self.__pieces.append('<a href="%s">' % cgi_escape(attrs['href']))
            else:
                self.__pieces.append('<a>')
        else:
            self.__pieces.append('<%s>' % tag)

    def handle_endtag(self, tag):
        if tag == self.__current:
            self.__pieces.append('</%s>' % tag)
            self.__current = None

    def handle_data(self, data):
        self.__pieces.append(cgi_escape(data))

    def handle_entityref(self, name):  # pragma: no cover
        if name in ('lt', 'gt', 'amp', 'quot'):
            self.__pieces.append('&%s;' % name)
        else:
            codepoint = htmlentitydefs.name2codepoint.get(name)
            if codepoint:
                self.__pieces.append(unichr(codepoint))
            else:
                self.__pieces.append('&amp;%s;' % name)

    def handle_charref(self, name):  # pragma: no cover
        name = name.lower()
        try:
            if name.startswith('x'):
                codepoint = int(name[1:], 16)
            else:
                codepoint = int(name)
            self.__pieces.append(cgi_escape(unichr(codepoint)))
        except (OverflowError, ValueError):
            self.__pieces.append('&amp;#%s;' % name)


def sanitize(text, strip=False):
    """Sanitize (or optionally entirely strip) HTML for use in Telegram."""

    return _HTMLSanitizer().sanitize(text, strip=strip)
