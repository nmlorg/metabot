"""Tests for metabot.util.pickle."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot import util


def test_optimize_simple():
    """Verify the optimizer preserves simple objects."""

    assert util.pickle.optimize(b'str') == b'str'
    assert util.pickle.optimize(u'str') == u'str'
    assert util.pickle.optimize({b'a': 1}) == {b'a': 1}
    assert util.pickle.optimize([1, 2]) == [1, 2]
    assert util.pickle.optimize((1, 2)) == (1, 2)
    assert util.pickle.optimize(1) == 1


def test_optimize_strings():
    """Verify the optimizer normalizes and dedupes strings."""

    bytes_1 = b'str ' + b'test'
    bytes_2 = b'str ' + b'test'
    assert bytes_1 is not bytes_2

    unicode_1 = u'str ' + u'test'
    unicode_2 = u'str ' + u'test'
    assert unicode_1 is not unicode_2

    store = {}

    optimized_str = util.pickle.optimize(bytes_1, store=store)
    assert util.pickle.optimize(bytes_2, store=store) is optimized_str
    optimized_uni = util.pickle.optimize(unicode_1, store=store)
    assert util.pickle.optimize(unicode_2, store=store) is optimized_uni


def test_optimize_containers():
    """Verify the optimizer doesn't break linkages by recreating containers."""

    key1 = u'key ' + u'test'
    key2 = u'key ' + u'test'
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

    new = util.pickle.optimize(cont)
    assert new == cont
    (key1copy,) = tuple(new[u'dummy1'])
    (key2copy,) = tuple(new[u'dummy2'])
    assert key1copy is key2copy
    assert new[u'dummy1'][key1] is new[u'dummy2'][key2]


def test_load_nonexistent(tmpdir):
    """Verify the loader silently ignores nonexistent files."""

    tmpfile = tmpdir.join('test.pickle')
    assert util.pickle.load(tmpfile.strpath) is None


def test_load_empty(tmpdir):
    """Verify the loader silently ignores empty files."""

    tmpfile = tmpdir.join('test.pickle')
    tmpfile.write('')
    assert util.pickle.load(tmpfile.strpath) is None


def test_load_malformed(tmpdir):
    """Verify the loader silently ignores malformed files."""

    tmpfile = tmpdir.join('test.pickle')
    tmpfile.write('bogus data')
    assert util.pickle.load(tmpfile.strpath) is None


def test_dump_simple(tmpdir):
    """Verify the dumper preserves simple objects."""

    tmpfile = tmpdir.join('test.pickle')
    obj = 1
    assert util.pickle.dump(tmpfile.strpath, obj) == obj
    assert tmpfile.load() == obj


def test_dump_load(tmpdir):
    """Verify the dumper and loader work as expected."""

    tmpfile = tmpdir.join('test.pickle')
    obj = {b'key': [b'value', b'value']}
    assert util.pickle.dump(tmpfile.strpath, obj) == obj
    assert util.pickle.load(tmpfile.strpath) == obj
