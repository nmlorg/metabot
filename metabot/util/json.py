"""Simplified interface to https://docs.python.org/3/library/json.html."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json

try:
    JSONDecodeError = json.decoder.JSONDecodeError  # pylint: disable=invalid-name
except AttributeError:  # pragma: no cover (Python 2)
    JSONDecodeError = ValueError


def load(fname):
    """Load fname as a JSON file, silently returning None on any error."""

    try:
        data = open(fname).read()
    except IOError:
        return

    try:
        return json.loads(data)
    except JSONDecodeError:
        pass


def dump(fname, obj):
    """Save obj as a JSON file to fname."""

    data = json.dumps(obj, indent=4, sort_keys=True).encode('ascii')
    with open(fname, 'wb') as fobj:
        fobj.write(data)
    return obj
