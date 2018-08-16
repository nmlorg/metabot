"""Tests for metabot.util.json."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot import util


def test_load_nonexistent(tmpdir):
    """Verify the loader silently ignores nonexistent files."""

    tmpfile = tmpdir.join('test.json')
    assert util.json.load(tmpfile.strpath) is None


def test_load_empty(tmpdir):
    """Verify the loader silently ignores empty files."""

    tmpfile = tmpdir.join('test.json')
    tmpfile.write('')
    assert util.json.load(tmpfile.strpath) is None


def test_load_malformed(tmpdir):
    """Verify the loader silently ignores malformed files."""

    tmpfile = tmpdir.join('test.json')
    tmpfile.write('bogus data')
    assert util.json.load(tmpfile.strpath) is None


def test_dump_simple(tmpdir):
    """Verify the dumper preserves simple objects."""

    tmpfile = tmpdir.join('test.json')
    obj = 123
    assert util.json.dump(tmpfile.strpath, obj) == obj
    assert tmpfile.read() == '123'


def test_dump_load(tmpdir):
    """Verify the dumper and loader work as expected."""

    tmpfile = tmpdir.join('test.json')
    obj = {'key': ['value', 'value']}
    assert util.json.dump(tmpfile.strpath, obj) == obj
    assert util.json.load(tmpfile.strpath) == obj
