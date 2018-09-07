"""Tests for metabot.calendars.loader."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import pickle

from metabot.calendars import loader


def test_loader(monkeypatch, tmpdir):
    """Run through loader.get."""

    # pylint: disable=protected-access
    monkeypatch.setattr(loader._CachingCalendarMixin, '_cache_dir', tmpdir.strpath)
    fname = tmpdir.strpath + '/3ccaceeb.pickle'
    with open(fname, 'wb') as cachefile:
        cachefile.write(pickle.dumps({'test_value': 1}))
    cal = loader.get('static:alpha@example.com')
    assert cal._CachingCalendarMixin__fname == fname
    assert cal.test_value == 1
    os.remove(fname)

    assert not cal.poll()
    assert not os.path.exists(fname)

    cal.poll_result = True
    assert cal.poll()
    assert os.path.exists(fname)
    os.remove(fname)

    local = cal.add({
        'start': 1000,
        'end': 2000,
    })
    assert local
    assert os.path.exists(fname)
    os.remove(fname)

    assert cal.update(local['local_id'], {'summary': 'new summary'})
    assert os.path.exists(fname)
    os.remove(fname)

    cal.remove(local['local_id'])
    assert os.path.exists(fname)
    os.remove(fname)
