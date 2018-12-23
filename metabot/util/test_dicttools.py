"""Tests for metabot.util.dicttools."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.util import dicttools


def test_audit():
    """Test the audit logging logic."""

    cont = dicttools.ImplicitTrackingDict()
    assert cont.finalize() == {}

    cont['alpha'] = 5
    assert cont.finalize() == {('alpha',): (5, None)}

    cont['alpha'] = 6
    assert cont.finalize() == {('alpha',): (6, 5)}

    cont['alpha'] = 6
    assert cont.log == {}

    cont['alpha'] = 7
    assert cont.log == {('alpha',): (7, 6)}

    cont['alpha'] = 7
    assert cont.log == {('alpha',): (7, 6)}

    cont['alpha'] = 8
    assert cont.log == {('alpha',): (8, 6)}

    cont['alpha'] = 6
    assert cont.log == {}


def test_pop():
    """Test ImplicitTrackingDict.pop."""

    cont = dicttools.ImplicitTrackingDict({'alpha': 'bravo'})
    assert cont.finalize() == {('alpha',): ('bravo', None)}

    assert cont.pop('unset') is None
    assert cont.finalize() == {}

    del cont['unset']
    assert cont.finalize() == {}

    assert cont.pop('alpha') == 'bravo'
    assert cont.finalize() == {('alpha',): (None, 'bravo')}


def test_setitem():
    """Test ImplicitTrackingDict.__setitem__."""

    cont = dicttools.ImplicitTrackingDict()
    assert cont.log == {}

    cont['alpha'] = {}
    assert cont.log == {}
    assert isinstance(cont['alpha'], dicttools.ImplicitTrackingDict)
    assert cont['alpha'].log is cont.log

    cont['alpha']['bravo'] = {}
    assert cont.log == {}
    assert cont['alpha']['bravo'].log is cont.log

    cont['alpha']['bravo']['charlie'] = 5
    cont['alpha']['bravo']['delta'] = 6
    assert cont.finalize() == {
        ('alpha', 'bravo', 'charlie'): (5, None),
        ('alpha', 'bravo', 'delta'): (6, None)
    }

    cont['alpha'] = 7
    assert cont.finalize() == {
        ('alpha', 'bravo', 'charlie'): (None, 5),
        ('alpha', 'bravo', 'delta'): (None, 6),
        ('alpha',): (7, None)
    }

    cont['alpha'] = b'ascii'
    assert cont.finalize() == {('alpha',): ('ascii', 7)}

    cont['alpha'] = None
    assert cont.finalize() == {('alpha',): (None, 'ascii')}

    assert 'alpha' not in cont


def test_missing():
    """Test ImplicitTrackingDict.__missing__."""

    cont = dicttools.ImplicitTrackingDict()

    assert list(cont.items()) == []
    assert 'unset' not in cont
    assert list(iter(cont)) == []

    # __missing__
    unset = cont['unset']
    assert cont['unset'] is unset
    assert unset == {}
    assert isinstance(unset, dicttools.ImplicitTrackingDict)

    assert cont.finalize() == {}

    assert list(cont.items()) == []
    assert 'unset' not in cont
    assert list(iter(cont)) == []


def test_list():
    """Test TrackingList (via ImplicitTrackingDict.__setitem__)."""

    cont = dicttools.ImplicitTrackingDict()

    cont['alpha'] = [2, 4, 6]  # extend
    assert cont.finalize() == {('alpha',): ((2, 4, 6), ())}

    cont['alpha'].append(8)
    assert cont.finalize() == {('alpha',): ((2, 4, 6, 8), (2, 4, 6))}

    cont['alpha'][1] = 10
    assert cont.finalize() == {('alpha',): ((2, 10, 6, 8), (2, 4, 6, 8))}

    cont['alpha'][0] = 2
    assert cont.finalize() == {}

    cont['alpha'][0] = 3
    cont['alpha'][0] = 2
    assert cont.finalize() == {}

    assert cont['alpha'].pop(0) == 2
    assert cont.finalize() == {('alpha',): ((10, 6, 8), (2, 10, 6, 8))}

    cont['alpha'].sort()
    assert cont.finalize() == {('alpha',): ((6, 8, 10), (10, 6, 8))}

    cont['alpha'].remove(8)
    assert cont.finalize() == {('alpha',): ((6, 10), (6, 8, 10))}

    cont['alpha'].reverse()
    assert cont.finalize() == {('alpha',): ((10, 6), (6, 10))}

    cont['alpha'].insert(0, 20)
    assert cont.finalize() == {('alpha',): ((20, 10, 6), (10, 6))}

    cont['alpha'].clear()
    assert cont.finalize() == {('alpha',): ((), (20, 10, 6))}
