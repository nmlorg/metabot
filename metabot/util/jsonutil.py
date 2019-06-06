"""Simplified interface to https://docs.python.org/3/library/json.html."""

import json


def load(fname):
    """Load fname as a JSON file, silently returning None on any error."""

    try:
        data = open(fname).read()
    except IOError:
        return

    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        pass


def dump(fname, obj):
    """Save obj as a JSON file to fname."""

    data = json.dumps(obj, indent=4, sort_keys=True).encode('ascii')
    with open(fname, 'wb') as fobj:
        fobj.write(data)
    return obj
