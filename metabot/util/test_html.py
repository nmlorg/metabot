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
    assert html.sanitize('<a weird="true">text</a>') == '<a>text</a>'

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
