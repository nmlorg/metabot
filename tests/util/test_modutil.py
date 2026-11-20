"""Tests for metabot.util.modutil."""

from metabot import multibot
from metabot.util import modutil


def test_basic():
    """Quick test for load_modules."""

    modules = modutil.load_modules('metabot')
    assert multibot in modules
