"""Tests for metabot.util.eventutil."""

import datetime

import pytz

from metabot.util import eventutil


def test_basic(build_conversation):
    """Test basic functions."""

    conv = build_conversation()
    event = {
        'description': 'DESCRIPTION',
        'end': 3000,
        'local_id': 'LOCAL_ID',
        'location': 'LOCATION',
        'start': 2000,
        'summary': 'SUMMARY',
    }
    tzinfo = pytz.timezone('America/Los_Angeles')
    base = datetime.datetime.fromtimestamp(1000, tz=tzinfo)

    def gen():
        return f'\n{eventutil.format_event(conv.bot, event, tzinfo, base=base)}\n'

    assert gen() == """
<b>SUMMARY</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBMT0NBTF9JRCBBbWVyaWNhL0xvc19BbmdlbGVz">🔜 ¹⁶ ᵐⁱⁿ Wed 31ˢᵗ, 4:33–4:50ᵖᵐ</a> @ <a href="https://maps.google.com/maps?q=LOCATION">LOCATION</a>

DESCRIPTION
"""

    event['location'] = ''

    assert gen() == """
<b>SUMMARY</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBMT0NBTF9JRCBBbWVyaWNhL0xvc19BbmdlbGVz">🔜 ¹⁶ ᵐⁱⁿ Wed 31ˢᵗ, 4:33–4:50ᵖᵐ</a>

DESCRIPTION
"""

    event['location'] = 'example.com/invite-code'

    assert gen() == """
<b>SUMMARY</b>
<a href="https://t.me/modulestestbot?start=L2V2ZW50cyBMT0NBTF9JRCBBbWVyaWNhL0xvc19BbmdlbGVz">🔜 ¹⁶ ᵐⁱⁿ Wed 31ˢᵗ, 4:33–4:50ᵖᵐ</a> @ <a href="https://example.com/invite-code">example.com/invite-code</a>

DESCRIPTION
"""
