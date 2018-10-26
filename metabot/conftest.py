"""Test environment defaults."""

from __future__ import absolute_import, division, print_function, unicode_literals

from ntelebot.conftest import _bot_mock  # pylint: disable=unused-import
import pytest


@pytest.fixture(autouse=True)
def _dont_mangle_callback_data(monkeypatch):
    monkeypatch.setattr('metabot.util.msgbuilder.MessageBuilder.CALLBACK_DATA_MAX', 0)
