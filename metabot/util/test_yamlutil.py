"""Tests for metabot.util.yamlutil."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import yamlutil


def test_load_nonexistent(tmpdir):
    """Verify the loader silently ignores nonexistent files."""

    tmpfile = tmpdir.join('test.yaml')
    assert yamlutil.load(tmpfile.strpath) is None


def test_load_empty(tmpdir):
    """Verify the loader silently ignores empty files."""

    tmpfile = tmpdir.join('test.yaml')
    tmpfile.write('')
    assert yamlutil.load(tmpfile.strpath) is None


def test_load_malformed(tmpdir):
    """Verify the loader silently ignores malformed files."""

    tmpfile = tmpdir.join('test.yaml')
    tmpfile.write('[')
    assert yamlutil.load(tmpfile.strpath) is None


def test_dump_simple(tmpdir):
    """Verify the dumper preserves simple objects."""

    tmpfile = tmpdir.join('test.yaml')
    obj = 123
    assert yamlutil.dump(tmpfile.strpath, obj) == obj
    assert tmpfile.read() == '123\n...\n'


def test_dump_load(tmpdir):
    """Verify the dumper and loader work as expected."""

    tmpfile = tmpdir.join('test.yaml')
    obj = {'key': ['value', 'value']}
    assert yamlutil.dump(tmpfile.strpath, obj) == obj
    assert yamlutil.load(tmpfile.strpath) == obj
