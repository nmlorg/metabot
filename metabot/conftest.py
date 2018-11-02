"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from ntelebot.conftest import _bot_mock  # pylint: disable=unused-import


@pytest.fixture(autouse=True)
def _dont_mangle_callback_data(monkeypatch):
    monkeypatch.setattr('ntelebot.keyboardutil.fix', lambda keyboard, maxlen=0: None)
