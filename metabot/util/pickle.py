"""Simplified interface to https://docs.python.org/2/library/pickle.html."""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import cPickle as pickle
except ImportError:
    import pickle
import pickletools

try:
    unicode
except NameError:
    unicode = str  # pylint: disable=invalid-name,redefined-builtin

try:
    dict.iteritems
except AttributeError:

    def iteritems(obj):  # pylint: disable=missing-docstring
        return obj.items()
else:  # pragma: no cover

    def iteritems(obj):  # pylint: disable=missing-docstring
        return obj.iteritems()


def load(fname):
    """Load fname as a Pickle file, silently returning None on any error."""

    try:
        data = open(fname, 'rb').read()
    except IOError:
        return

    try:
        return pickle.loads(data)
    except (EOFError, pickle.UnpicklingError):
        pass


def optimize(obj, store=None):
    """Return a copy of obj with normalized and deduplicated strings."""

    if store is None:
        store = {}

    opt = lambda obj: optimize(obj, store=store)

    if isinstance(obj, dict):
        new = [(opt(k), opt(v)) for k, v in iteritems(obj)]
        obj.clear()
        obj.update(new)
        return obj
    if isinstance(obj, list):
        for i, value in enumerate(obj):
            obj[i] = opt(value)
        return obj
    if isinstance(obj, tuple):
        return tuple(map(opt, obj))
    if isinstance(obj, (bytes, unicode)):
        new = store.get(obj)
        if new is None:
            store[obj] = new = obj
        return new
    return obj


def dump(fname, obj, store=None):
    """Optimize obj, then save it as a Pickle file to fname."""

    obj = optimize(obj, store=store)
    data = pickletools.optimize(pickle.dumps(obj, -1))
    with open(fname, 'wb') as fobj:
        fobj.write(data)
    return obj
