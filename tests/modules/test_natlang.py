"""Tests for metabot.modules.natlang."""

import pytest

from metabot.calendars import loader
from metabot.modules import natlang


@pytest.fixture
def conversation(build_conversation):  # pylint: disable=missing-docstring
    return build_conversation(natlang)


# pylint: disable=line-too-long


def test_simple(conversation, monkeypatch):  # pylint: disable=redefined-outer-name
    """Verify the natlang module."""

    assert conversation.message('When is the next sock hop?') == ''

    monkeypatch.setattr('time.time', lambda: 1 * 60 * 60.)

    other_cal = loader.get('static:other_cal')
    assert other_cal.calcode == '2a366983'
    other_cal.events = {
        '2a366983:alpha': {
            'description': 'Alpha Description',
            'end': 3 * 60 * 60,
            'local_id': '2a366983:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 2 * 60 * 60,
            'summary': 'Other Sock Hop',
        },
    }
    conversation.multibot.multical.add('static:other_cal')
    conversation.multibot.calendars['2a366983'] = {'name': 'Other Group'}

    my_cal = loader.get('static:my_cal')
    assert my_cal.calcode == 'fc2d5e05'
    my_cal.events = {
        'fc2d5e05:bravo': {
            'description': '',
            'end': 5 * 60 * 60,
            'local_id': 'fc2d5e05:bravo',
            'location': 'My Venue, Rest of My Location',
            'start': 4 * 60 * 60,
            'summary': 'My Sock Hop',
        },
        'fc2d5e05:charlie': {
            'description': '',
            'end': 7 * 60 * 60,
            'local_id': 'fc2d5e05:charlie',
            'location': 'My Venue, Rest of My Location',
            'start': 6 * 60 * 60,
            'summary': 'My Sock Hop',
        },
        'fc2d5e05:delta': {
            'description': '',
            'end': 9 * 60 * 60,
            'local_id': 'fc2d5e05:delta',
            'location': 'My Venue, Rest of My Location',
            'start': 8 * 60 * 60,
            'summary': 'Special Sock Hop',
        },
        'fc2d5e05:echo': {
            'description': '',
            'end': 11 * 60 * 60,
            'local_id': 'fc2d5e05:echo',
            'location': 'My Venue, Rest of My Location',
            'start': 1 * 60 * 600,
            'summary': 'My Sock Hop',
        },
        'fc2d5e05:foxtrot': {
            'description': '',
            'end': 13 * 60 * 60,
            'local_id': 'fc2d5e05:foxtrot',
            'location': 'Alternate Venue, Rest of Alternate Location',
            'start': 12 * 60 * 60,
            'summary': 'My Sock Hop',
        },
    }
    conversation.multibot.multical.add('static:my_cal')
    conversation.multibot.calendars['fc2d5e05'] = {'name': 'My Group'}

    conversation.mgr.bot_conf['events']['users']['1000']['calendars'] = 'fc2d5e05'

    assert conversation.message('When is the next sock hop?') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<i>The next sock hop is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpicmF2byBVVEM">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 4–5ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next Special Sock Hop is:</i>

<b>Special Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpkZWx0YSBVVEM">🔜 ⁷ ʰᵒᵘʳˢ Thu 1ˢᵗ, 8–9ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next sock hop at Alternate Venue is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpmb3h0cm90IFVUQw">🔜 ¹¹ ʰᵒᵘʳˢ Thu 1ˢᵗ, 12–1ᵖᵐ</a> @ <a href="https://maps.google.com/maps?q=Alternate+Venue%2C+Rest+of+Alternate+Location">Alternate Venue</a>
"""

    assert conversation.message('Where is the next my sock hop?') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<i>The next my sock hop is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpicmF2byBVVEM">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 4–5ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next my sock hop at Alternate Venue is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpmb3h0cm90IFVUQw">🔜 ¹¹ ʰᵒᵘʳˢ Thu 1ˢᵗ, 12–1ᵖᵐ</a> @ <a href="https://maps.google.com/maps?q=Alternate+Venue%2C+Rest+of+Alternate+Location">Alternate Venue</a>
"""

    assert conversation.message('When is the next sock hop at my venue?') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<i>The next sock hop at my venue is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpicmF2byBVVEM">🔜 ³ ʰᵒᵘʳˢ Thu 1ˢᵗ, 4–5ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next Special Sock Hop at my venue is:</i>

<b>Special Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpkZWx0YSBVVEM">🔜 ⁷ ʰᵒᵘʳˢ Thu 1ˢᵗ, 8–9ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>
"""
