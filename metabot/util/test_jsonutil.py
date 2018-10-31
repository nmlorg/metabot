"""Tests for metabot.util.jsonutil."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import jsonutil


def test_load_nonexistent(tmpdir):
    """Verify the loader silently ignores nonexistent files."""

    tmpfile = tmpdir.join('test.json')
    assert jsonutil.load(tmpfile.strpath) is None


def test_load_empty(tmpdir):
    """Verify the loader silently ignores empty files."""

    tmpfile = tmpdir.join('test.json')
    tmpfile.write('')
    assert jsonutil.load(tmpfile.strpath) is None


def test_load_malformed(tmpdir):
    """Verify the loader silently ignores malformed files."""

    tmpfile = tmpdir.join('test.json')
    tmpfile.write('bogus data')
    assert jsonutil.load(tmpfile.strpath) is None


def test_dump_simple(tmpdir):
    """Verify the dumper preserves simple objects."""

    tmpfile = tmpdir.join('test.json')
    obj = 123
    assert jsonutil.dump(tmpfile.strpath, obj) == obj
    assert tmpfile.read() == '123'


def test_dump_load(tmpdir):
    """Verify the dumper and loader work as expected."""

    tmpfile = tmpdir.join('test.json')
    obj = {'key': ['value', 'value']}
    assert jsonutil.dump(tmpfile.strpath, obj) == obj
    assert jsonutil.load(tmpfile.strpath) == obj
