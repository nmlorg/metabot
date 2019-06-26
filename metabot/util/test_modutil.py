"""Tests for metabot.util.modutil."""

from metabot import conftest
from metabot import multibot
from metabot import test_multibot
from metabot.util import modutil


def test_basic():
    """Quick test for load_modules."""

    modules = modutil.load_modules('metabot')
    assert conftest not in modules
    assert multibot in modules
    assert test_multibot not in modules
