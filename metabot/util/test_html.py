"""Tests for metabot.util.html."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import html


def test_sanitize():
    """Test sanitization logic."""

    assert html.sanitize('') == ''
    assert html.sanitize('empty') == 'empty'
    assert html.sanitize('&#8592; &#x2190; &larr;') == '\u2190 \u2190 \u2190'
    assert html.sanitize('&#38; &#x26; &amp;') == '&amp; &amp; &amp;'

    # From https://core.telegram.org/bots/api#formatting-options.
    text = """
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
"""
    assert html.sanitize(text) == text
    assert html.sanitize('a<br>b<div>c</div><p>d</p>') == 'a\nb\nc\nd'
    assert html.sanitize('<a weird="true">text</a>') == '<a>text</a>'

    assert html.sanitize('<b>good</b> <span>bad</span>') == '<b>good</b> bad'
    assert html.sanitize('<b><span>nested</span></b>') == '<b>nested</b>'
    assert html.sanitize('<span><b>nested</b></span>') == '<b>nested</b>'
    assert html.sanitize('<b>broken <i>good</i>') == '<b>broken </b><i>good</i>'

    assert html.sanitize('&bogus;') == '&amp;bogus;'
    assert html.sanitize('&#bogus;') == '&amp;#bogus;'
    assert html.sanitize('&#xxbogus;') == '&amp;#xxbogus;'


def test_strip():
    """Test stripping logic."""

    assert html.sanitize('', True) == ''
    assert html.sanitize('empty', True) == 'empty'
    assert html.sanitize('&#8592; &#x2190; &larr;', True) == '\u2190 \u2190 \u2190'
    assert html.sanitize('&#38; &#x26; &amp;', True) == '&amp; &amp; &amp;'

    # From https://core.telegram.org/bots/api#formatting-options.
    text = """
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
"""
    assert html.sanitize(text, True) == """
bold, bold
italic, italic
inline URL
inline mention of a user
inline fixed-width code
pre-formatted fixed-width code block
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
