"""Tests for metabot.modules.globalrecords."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from metabot.modules import globalrecords


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(globalrecords)


# pylint: disable=line-too-long


def test_dummy(conversation):  # pylint: disable=redefined-outer-name
    """Test basic logging."""

    assert not conversation.multibot.conf['groups']
    assert not conversation.multibot.conf['users']

    assert conversation.message('/dummy') == []

    assert not conversation.multibot.conf['groups']
    assert conversation.multibot.conf['users'] == {
        1000: {
            'first_name': 'User1000',
            'name': 'User1000',
            'username': 'user1000',
        },
    }

    assert conversation.message('/dummy', last_name='Lastington') == []

    assert not conversation.multibot.conf['groups']
    assert conversation.multibot.conf['users'] == {
        1000: {
            'first_name': 'User1000',
            'last_name': 'Lastington',
            'name': 'User1000 Lastington',
            'username': 'user1000',
        },
    }

    assert conversation.message('/dummy', last_name='Lastington', chat_type='supergroup') == []

    assert conversation.multibot.conf['groups'] == {
        -1001000001000: {
            'title': 'Group Chat',
            'type': 'supergroup',
        },
    }
    assert conversation.multibot.conf['users'] == {
        1000: {
            'first_name': 'User1000',
            'last_name': 'Lastington',
            'name': 'User1000 Lastington',
            'username': 'user1000',
        },
    }
