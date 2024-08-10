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

    def handle_starttag(self, tag, attrs):  # pylint: disable=too-many-branches,too-many-return-statements
        if self.__remaining is not None and not self.__remaining:
            return
        if tag in ('br', 'div', 'p'):
            self.__append('\n')
            return
        if self.__strip:
            return
        if tag in self.naked:
            self.__stack.append(tag)
            self.__pieces.append(f'<{tag}>')
            return
        if tag not in self.coupled:
            return

        attrs = dict(attrs)
        attribute_name = self.coupled[tag]
        attribute_value = attrs.get(attribute_name, '')

        # pylint: disable=line-too-long
        # if (tag_name == "a" && attribute_name == Slice("href")) {
        #   argument = std::move(attribute_value);
        # } else if (tag_name == "code" && attribute_name == Slice("class") &&
        #            begins_with(attribute_value, "language-")) {
        #   argument = attribute_value.substr(9);
        # } else if (tag_name == "span" && attribute_name == Slice("class") && begins_with(attribute_value, "tg-")) {
        #   argument = attribute_value.substr(3);
        # } else if (tag_name == "tg-emoji" && attribute_name == Slice("emoji-id")) {
        #   argument = std::move(attribute_value);
        # } else if (tag_name == "blockquote" && attribute_name == Slice("expandable")) {
        #   argument = "1";
        # }
        argument = None
        if tag == 'a':
            argument = attribute_value
        elif tag == 'code' and attribute_value.startswith('language-'):
            argument = attribute_value[9:]
        elif tag == 'span' and attribute_value.startswith('tg-'):
            argument = attribute_value[3:]
        elif tag == 'tg-emoji':
            argument = attribute_value
        elif tag == 'blockquote' and 'expandable' in attrs:
            argument = '1'

        # if (tag_name == "span" && argument != "spoiler") {
        #   return Status::Error(400, PSLICE()
        #                                 << "Tag \"span\" must have class \"tg-spoiler\" at byte offset " << begin_pos);
        # }
        if tag == 'span' and argument != 'spoiler':
            return

        # } else if (tag_name == "tg-emoji") {
        #   auto r_document_id = to_integer_safe<int64>(nested_entities.back().argument);
        #   if (r_document_id.is_error() || r_document_id.ok() == 0) {
        #     return Status::Error(400, "Invalid custom emoji identifier specified");
        #   }
        if tag == 'tg-emoji' and (not argument.isdigit() or not 0 < int(argument) < 2**63):
            return

        if tag == 'a' and not argument:
            return

        self.__stack.append(tag)
        if not argument:
            self.__pieces.append(f'<{tag}>')
        elif not attribute_value:
            self.__pieces.append(f'<{tag} {attribute_name}>')
        else:
            self.__pieces.append(f'<{tag} {attribute_name}="{escape(attribute_value)}">')

    def handle_endtag(self, tag):
        if tag and tag not in self.__stack:
            return

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
