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

    monkeypatch.setattr('time.time', lambda: 1000.)

    other_cal = loader.get('static:other_cal')
    assert other_cal.calcode == '2a366983'
    other_cal.events = {
        '2a366983:alpha': {
            'description': 'Alpha Description',
            'end': 3000,
            'local_id': '2a366983:alpha',
            'location': 'Alpha Venue, Rest of Alpha Location',
            'start': 2000,
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
            'end': 5000,
            'local_id': 'fc2d5e05:bravo',
            'location': 'My Venue, Rest of My Location',
            'start': 4000,
            'summary': 'My Sock Hop',
        },
        'fc2d5e05:charlie': {
            'description': '',
            'end': 7000,
            'local_id': 'fc2d5e05:charlie',
            'location': 'My Venue, Rest of My Location',
            'start': 6000,
            'summary': 'Special Sock Hop',
        },
        'fc2d5e05:delta': {
            'description': '',
            'end': 9000,
            'local_id': 'fc2d5e05:delta',
            'location': 'Alternate Venue, Rest of Special Location',
            'start': 8000,
            'summary': 'Alternate Sock Hop',
        },
    }
    conversation.multibot.multical.add('static:my_cal')
    conversation.multibot.calendars['fc2d5e05'] = {'name': 'My Group'}

    conversation.bot.config['issue37']['events']['users']['1000']['calendars'] = 'fc2d5e05'

    assert conversation.message('When is the next sock hop?') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<i>The next sock hop I know about is:</i>

<b>Other Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyAyYTM2Njk4MzphbHBoYSBVVEM">TODAY, Thu 1ˢᵗ, 12:33–12:50ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alpha+Venue%2C+Rest+of+Alpha+Location">Alpha Venue</a>

<i>The next sock hop on the My Group calendar is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpicmF2byBVVEM">TODAY, Thu 1ˢᵗ, 1:06–1:23ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next Special Sock Hop is:</i>

<b>Special Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpjaGFybGllIFVUQw">TODAY, Thu 1ˢᵗ, 1:40–1:56ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>

<i>The next sock hop at Alternate Venue is:</i>

<b>Alternate Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpkZWx0YSBVVEM">TODAY, Thu 1ˢᵗ, 2:13–2:30ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=Alternate+Venue%2C+Rest+of+Special+Location">Alternate Venue</a>
"""

    assert conversation.message('When is the next my sock hop?') == """\
[chat_id=1000 disable_web_page_preview=True parse_mode=HTML]
<i>The next my sock hop is:</i>

<b>My Sock Hop</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBmYzJkNWUwNTpicmF2byBVVEM">TODAY, Thu 1ˢᵗ, 1:06–1:23ᵃᵐ</a> @ <a href="https://maps.google.com/maps?q=My+Venue%2C+Rest+of+My+Location">My Venue</a>
"""
