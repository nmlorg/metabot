"""Tests for metabot.util.html."""

from metabot.util import html


def test_sanitize():
    """Test sanitization logic."""

    assert html.sanitize('') == ''
    assert html.sanitize('empty') == 'empty'
    assert html.sanitize('&#8592; &#x2190; &larr; \u2190') == '← ← ← ←'
    assert html.sanitize('&#38; &#x26; &amp;') == '&amp; &amp; &amp;'

    # From https://core.telegram.org/bots/api#formatting-options.
    text = """
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
<blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>
"""
    assert html.sanitize(text) == text
    assert html.sanitize('a<br>b<div>c</div><p>d</p>') == 'a\nb\nc\nd'
    assert html.sanitize('<code weird="true">text</code>') == '<code>text</code>'

    assert html.sanitize('<b>good</b> <bogus>bad</bogus>') == '<b>good</b> bad'
    assert html.sanitize('<b><bogus>nested</bogus></b>') == '<b>nested</b>'
    assert html.sanitize('<bogus><b>nested</b></bogus>') == '<b>nested</b>'
    assert html.sanitize('<b>broken <i>good</i>') == '<b>broken <i>good</i></b>'

    assert html.sanitize('&bogus;') == '&amp;bogus;'
    assert html.sanitize('&#bogus;') == '&amp;#bogus;'
    assert html.sanitize('&#xxbogus;') == '&amp;#xxbogus;'


def test_strip():
    """Test stripping logic."""

    assert html.sanitize('', True) == ''
    assert html.sanitize('empty', True) == 'empty'
    assert html.sanitize('&#8592; &#x2190; &larr; \u2190', True) == '← ← ← ←'
    assert html.sanitize('&#38; &#x26; &amp;', True) == '&amp; &amp; &amp;'

    # From https://core.telegram.org/bots/api#formatting-options.
    text = """
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
<blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>
"""
    assert html.sanitize(text, True) == """
bold, bold
italic, italic
underline, underline
strikethrough, strikethrough, strikethrough
spoiler, spoiler
bold italic bold italic bold strikethrough italic bold strikethrough spoiler underline italic bold bold
inline URL
inline mention of a user
👍
inline fixed-width code
pre-formatted fixed-width code block
pre-formatted fixed-width code block written in the Python programming language
Block quotation started\nBlock quotation continued\nThe last line of the block quotation
Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation
"""
    assert html.sanitize('first<br>second', True) == 'first\nsecond'
    assert html.sanitize('<a weird="true">text</a>', True) == 'text'

    assert html.sanitize('<b>good</b> <span>bad</span>', True) == 'good bad'
    assert html.sanitize('<b><span>nested</span></b>', True) == 'nested'
    assert html.sanitize('<span><b>nested</b></span>', True) == 'nested'
    assert html.sanitize('<b>broken <i>good</i>', True) == 'broken good'

    assert html.sanitize('&bogus;', True) == '&amp;bogus;'
    assert html.sanitize('&#bogus;', True) == '&amp;#bogus;'
    assert html.sanitize('&#xxbogus;', True) == '&amp;#xxbogus;'


def test_truncate():
    """Test truncating logic."""

    assert html.truncate('', 10) == ''
    assert html.truncate('123456789012345', 10) == '1234567890'
    assert html.truncate('<b>123456789012345</b>', 10) == '<b>1234567890</b>'
    assert html.truncate('123<b>456<i>789012345', 10) == '123<b>456<i>7890</i></b>'
    assert html.truncate('&lt;' * 100, 10) == '&lt;' * 10
    assert html.truncate('&#x2022;' * 100, 10) == '\u2022' * 10

    # I originally had a short circuit in _HTMLSanitizer.__append:
    #   if len(data) <= self.__remaining:
    #       self.__remaining -= len(data)
    #       return self.__pieces.append(data)
    # which would overcount the lengths of entities if they were part of a fragment that otherwise
    # didn't trip the length limit. So this would work because the fragment tripped the limit:
    assert html.truncate('&lt;2345678901234567890', 10) == '&lt;234567890'
    # but this would truncate to '&lt;2345<b>67</b>' because it counted '&lt;' as 4 instead of 1
    # while processing '&lt;2345':
    assert html.truncate('&lt;2345<b>678901234567890', 10) == '&lt;2345<b>67890</b>'


def test_MessageEntity_cpp_quirks():  # pylint: disable=invalid-name
    """Verify sync with https://github.com/tdlib/td/blob/master/td/telegram/MessageEntity.cpp."""

    assert html.sanitize('<a foo=1 href=2 bar=3>b</a>') == '<a href="2">b</a>'
    # Technically, '<a>https://example.com/</a>' would be considered valid, but I don't want to
    # have to validate URLs.
    assert html.sanitize('<a foo=1 bar=3>b</a>') == 'b'

    assert html.sanitize('<SPAN CLASS="tg-spoiler">x</span>') == '<span class="tg-spoiler">x</span>'
    assert html.sanitize('<span class="other">x</span>') == 'x'
    assert html.sanitize('<span>x</span>') == 'x'

    assert html.sanitize('<blockquote>quote</blockquote>') == '<blockquote>quote</blockquote>'
    assert html.sanitize(
        '<blockquote other=1>quote</blockquote>') == '<blockquote>quote</blockquote>'
    assert html.sanitize(
        '<blockquote expandable>quote</blockquote>') == '<blockquote expandable>quote</blockquote>'
    assert html.sanitize('<blockquote expandable=true>quote</blockquote>'
                        ) == '<blockquote expandable="true">quote</blockquote>'

    assert html.sanitize('<tg-emoji>emoji</tg-emoji>') == 'emoji'
    assert html.sanitize(
        '<tg-emoji emoji-id=1>emoji</tg-emoji>') == '<tg-emoji emoji-id="1">emoji</tg-emoji>'
    assert html.sanitize('<tg-emoji emoji-id=0>emoji</tg-emoji>') == 'emoji'
    assert html.sanitize('<tg-emoji emoji-id=10000000000000000000>emoji</tg-emoji>') == 'emoji'
    assert html.sanitize('<tg-emoji emoji-id=dummy>emoji</tg-emoji>') == 'emoji'

    assert html.sanitize('<code>code</code>') == '<code>code</code>'
    assert html.sanitize(
        '<code class="language-python">code</code>') == '<code class="language-python">code</code>'
    assert html.sanitize('<code class="other">code</code>') == '<code>code</code>'


def test_wellformed_close():
    """Verify well-formed but Telegram-incompatible markup does not close other tags."""

    assert html.sanitize(
        'hi <code>there <span>friend</span> still') == 'hi <code>there friend still</code>'
