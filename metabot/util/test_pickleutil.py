"""Tests for metabot.util.pickleutil."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

from metabot.util import pickleutil


def test_optimize_simple():
    """Verify the optimizer preserves simple objects."""

    assert pickleutil.optimize(b'str') == b'str'
    assert pickleutil.optimize(u'str') == u'str'
    assert pickleutil.optimize({b'a': 1}) == {b'a': 1}
    assert pickleutil.optimize([1, 2]) == [1, 2]
    assert pickleutil.optimize((1, 2)) == (1, 2)
    assert pickleutil.optimize(1) == 1


def test_optimize_strings():
    """Verify the optimizer normalizes and dedupes strings."""

    bytes_1 = json.loads('"str test"').encode('ascii')
    bytes_2 = json.loads('"str test"').encode('ascii')
    assert bytes_1 == bytes_2 and bytes_1 is not bytes_2

    unicode_1 = json.loads('"str test"')
    unicode_2 = json.loads('"str test"')
    assert unicode_1 == unicode_2 and unicode_1 is not unicode_2

    store = {}

    optimized_str = pickleutil.optimize(bytes_1, store=store)
    assert pickleutil.optimize(bytes_2, store=store) is optimized_str
    optimized_uni = pickleutil.optimize(unicode_1, store=store)
    assert pickleutil.optimize(unicode_2, store=store) is optimized_uni


def test_optimize_containers():
    """Verify the optimizer doesn't break linkages by recreating containers."""

    key1 = json.loads('"key test"')
    key2 = json.loads('"key test"')
    assert key1 == key2 and key1 is not key2

    entry = {u'dummy': u'test'}
    cont = {
        u'dummy1': {
            key1: entry,
        },
        u'dummy2': {
            key2: entry,
        }
    }
    (key1copy,) = tuple(cont[u'dummy1'])
    (key2copy,) = tuple(cont[u'dummy2'])
    assert key1copy == key2copy and key1copy is not key2copy
    assert cont[u'dummy1'][key1] is cont[u'dummy2'][key2]

    new = pickleutil.optimize(cont)
    assert new == cont
    (key1copy,) = tuple(new[u'dummy1'])
    (key2copy,) = tuple(new[u'dummy2'])
    assert key1copy is key2copy
    assert new[u'dummy1'][key1] is new[u'dummy2'][key2]


def test_load_nonexistent(tmpdir):
    """Verify the loader silently ignores nonexistent files."""

    tmpfile = tmpdir.join('test.pickle')
    assert pickleutil.load(tmpfile.strpath) is None


def test_load_empty(tmpdir):
    """Verify the loader silently ignores empty files."""

    tmpfile = tmpdir.join('test.pickle')
    tmpfile.write('')
    assert pickleutil.load(tmpfile.strpath) is None


def test_load_malformed(tmpdir):
    """Verify the loader silently ignores malformed files."""

    tmpfile = tmpdir.join('test.pickle')
    tmpfile.write('bogus data')
    assert pickleutil.load(tmpfile.strpath) is None


def test_dump_simple(tmpdir):
    """Verify the dumper preserves simple objects."""

    tmpfile = tmpdir.join('test.pickle')
    obj = 1
    assert pickleutil.dump(tmpfile.strpath, obj) == obj
    assert tmpfile.load() == obj


def test_dump_load(tmpdir):
    """Verify the dumper and loader work as expected."""

    tmpfile = tmpdir.join('test.pickle')
    obj = {b'key': [b'value', b'value']}
    assert pickleutil.dump(tmpfile.strpath, obj) == obj
    assert pickleutil.load(tmpfile.strpath) == obj
