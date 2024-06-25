"""Announce upcoming events once a day."""

import datetime
import logging
import operator
import random
import re
import time

import ntelebot

from metabot.util import eventutil
from metabot.util import html
from metabot.util import humanize
from metabot.util import pickleutil


def modinit(multibot):  # pylint: disable=missing-docstring

    def _queue():
        multibot.loop.queue.puthourly(0, _hourly, jitter=random.random() * 5)

    if multibot.conf.confdir:
        recordsfname = multibot.conf.confdir + '/daily.pickle'
        records = pickleutil.load(recordsfname) or {}
    else:
        recordsfname = None
        records = {}

    def _hourly():
        try:
            multibot.multical.poll()
            _daily_messages(multibot, records)
            if recordsfname:
                pickleutil.dump(recordsfname, records)
        finally:
            _queue()

    _queue()


def _daily_messages(multibot, records):  # pylint: disable=too-many-branches,too-many-locals
    now = time.time()
    for botuser, botconf in multibot.conf['bots'].items():
        for groupid, groupconf in botconf['issue37']['moderator'].items():
            calcodes, tzinfo, count, days, hour, dow = eventutil.get_group_conf(groupconf)
            if not tzinfo or not isinstance(hour, int):
                continue
            # See https://github.com/nmlorg/metabot/issues/26.
            bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
            bot.multibot = multibot
            form = lambda event: eventutil.format_event(bot, event, tzinfo, full=False)  # pylint: disable=cell-var-from-loop
            nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
            key = (botuser, groupid)

            if nowdt.hour == hour and not dow & 1 << nowdt.weekday():
                sendnew = True
                eventtime = now
                eventdt = nowdt
            elif key in records:
                sendnew = False
                eventtime, lastevents, lastmessage = records[key]
                eventdt = datetime.datetime.fromtimestamp(eventtime, tzinfo)
            else:
                continue

            events, alerts = eventutil.get_group_events(bot, calcodes, tzinfo, count, days,
                                                        eventtime)
            _handle_alerts(bot, records, groupid, alerts)
            preambles = groupconf['daily'].get('text', '').splitlines()
            preamble = preambles and preambles[eventdt.toordinal() % len(preambles)] or ''

            message = None

            if sendnew:
                if events:
                    text = _format_daily_message(preamble, list(map(form, events)))
                    url = eventutil.get_image(events[0], botconf)
                    message = reminder_send(bot, groupid, text, url)
            else:
                edits = diff_events(multibot, tzinfo, lastevents, events)  # pylint: disable=possibly-used-before-assignment

                if not edits:
                    continue

                updtext = 'Updated:\n' + '\n'.join(edits)
                try:
                    updmessage = bot.send_message(
                        chat_id=groupid,
                        reply_to_message_id=lastmessage['message_id'],  # pylint: disable=possibly-used-before-assignment
                        text=updtext,
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        disable_notification=True)
                except ntelebot.errors.Error:
                    logging.exception('While sending to %s:\n%s', groupid, updtext)
                    continue

                updated = 'Updated ' + humanize.time(nowdt)
                groupidnum = int(groupid)
                if -1002147483647 <= groupidnum < -1000000000000:
                    updated = '<a href="https://t.me/c/%s/%s">%s</a>' % (
                        -1000000000000 - groupidnum, updmessage['message_id'], updated)
                else:
                    updated = '%s (%s)' % (updated, updmessage['message_id'])
                text = '%s\n\n[%s]' % (_format_daily_message(preamble, list(map(form,
                                                                                events))), updated)
                message = reminder_edit(bot, groupid, lastmessage['message_id'], text,
                                        lastmessage.get('caption'))

            if message:
                records[key] = (eventtime, [event.copy() for event in events], message)


def reminder_send(bot, groupid, text, photo):
    """Send a message with the given photo + caption, falling back to plain text."""

    if photo:
        try:
            return bot.send_photo(chat_id=groupid,
                                  photo=photo,
                                  caption=text,
                                  parse_mode='HTML',
                                  disable_notification=True)
        except ntelebot.errors.Error:  # See https://github.com/nmlorg/metabot/issues/76.
            logging.exception('Downgrading to plain text:')

    try:
        return bot.send_message(chat_id=groupid,
                                text=text,
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                disable_notification=True)
    except ntelebot.errors.Error:
        logging.exception('While sending to %s:\n%s', groupid, text)


def reminder_edit(bot, groupid, message_id, text, isphoto):
    """Edit a photo caption/plain message."""

    try:
        if isphoto:
            return bot.edit_message_caption(chat_id=groupid,
                                            message_id=message_id,
                                            caption=text,
                                            parse_mode='HTML')
        return bot.edit_message_text(chat_id=groupid,
                                     message_id=message_id,
                                     text=text,
                                     parse_mode='HTML',
                                     disable_web_page_preview=True)
    except ntelebot.errors.Error:
        logging.exception('While editing %s in %s:\n%s', message_id, groupid, text)


def diff_events(multibot, tzinfo, lastevents, events):  # pylint: disable=too-many-locals
    """Return a list of differences between lastevents and events."""

    lastmap = {event['local_id']: event for event in lastevents}
    curmap = {event['local_id']: event for event in events}
    bothevents = events.copy()
    bothevents.extend(event for event in lastevents if event['local_id'] not in curmap)
    bothevents.sort(key=operator.itemgetter('start', 'end', 'summary', 'local_id'))
    edits = []
    for event in bothevents:
        title = '  \u2022 ' + event['summary']
        lastevent = lastmap.get(event['local_id'])
        if not lastevent:
            edits.append(title)
            edits.append('    \u25e6 New event!')
            continue
        event = multibot.multical.get_event(event['local_id'])[1]
        if not event:
            edits.append(title)
            edits.append('    \u25e6 Removed.')
            continue
        pairs = (
            (lastevent['summary'], event['summary']),
            (eventutil.humanize_range(lastevent['start'], lastevent['end'], tzinfo),
             eventutil.humanize_range(event['start'], event['end'], tzinfo)),
            (lastevent['location'], event['location']),
            (html.sanitize(lastevent['description'], strip=True),
             html.sanitize(event['description'], strip=True)),
        )  # yapf: disable
        pieces = []
        for left, right in pairs:
            diff = _quick_diff(left, right)
            if diff:
                pieces.append(diff)
        if pieces:
            edits.append(title)
            for left, right in pieces:
                edits.append(f'      <s>{left}</s>')
                edits.append(f'      {right}')
    return edits


def _quick_diff(left, right):
    left = re.sub(r'https?://\S+', '', left)
    left = re.sub(r'\s+', ' ', left).strip()
    right = re.sub(r'https?://\S+', '', right)
    right = re.sub(r'\s+', ' ', right).strip()
    if left == right:
        return
    i = 0
    while i < len(left) and i < len(right) and right[i] == left[i]:
        i += 1
    if i > 10:
        left = '\u2026' + left[i - 9:]
        right = '\u2026' + right[i - 9:]
    if len(left) > 40:
        left = left[:39] + '\u2026'
    if len(right) > 40:
        right = right[:39] + '\u2026'
    return left, right


def _format_daily_message(preamble, events):
    if not events:
        return preamble or 'No upcoming events!'

    if len(events) == 1:
        text = "There's an event coming up:"
    elif len(events) == 2:
        text = 'There are a couple events coming up:'
    elif len(events) == 3:
        text = 'There are a few events coming up:'
    else:
        text = 'There are a bunch of events coming up:'
    if preamble and preamble.endswith(':') and 'events' in preamble.lower():
        text = preamble
    elif preamble:
        if preamble[-1] in ('.', '?', '!'):
            preamble += ' '
        else:
            preamble += ' \u2022 '
        text = text[0].lower() + text[1:]
        if 'event' in preamble.lower():
            text = 'Speaking of which, ' + text
        else:
            text = 'Also, ' + text
        text = preamble + text
    return '%s\n\n%s' % (text, '\n'.join(events))


def _handle_alerts(bot, records, groupid, alerts):
    # See https://github.com/nmlorg/metabot/issues/85.
    alerts = [
        alert for alert in alerts
        if alert['urgency'] in ('Immediate', 'Expected') and alert['severity'] in (
            'Extreme', 'Severe') and alert['certainty'] == 'Observed'
    ]

    text = _format_alerts(alerts)

    kwargs = {}
    key = ('alerts', groupid)
    if key in records:
        if not text:
            records.pop(key)
            return
        lasttext, lastmessage = records[key]
        if lasttext == text:
            return
        kwargs['reply_to_message_id'] = lastmessage['message_id']
    if text:
        message = None
        try:
            message = bot.send_message(chat_id=groupid,
                                       text=text,
                                       parse_mode='HTML',
                                       disable_web_page_preview=True,
                                       disable_notification=True,
                                       **kwargs)
        except ntelebot.errors.Error:
            logging.exception('While sending to %s:\n%s', groupid, text)
        if not message and kwargs:
            try:
                message = bot.send_message(chat_id=groupid,
                                           text=text,
                                           parse_mode='HTML',
                                           disable_web_page_preview=True,
                                           disable_notification=True)
            except ntelebot.errors.Error:
                logging.exception('While sending to %s:\n%s', groupid, text)
        if message:
            records[key] = (text, message)


def _format_alerts(alerts):
    if not alerts:
        return ''
    text = []
    for alert in alerts:
        text.append('<a href="https://alerts-v2.weather.gov/products/%s">%s %s</a>' %
                    (alert['id'], alert['event'], alert['id']))
        text.append('')
        desc = '%s\n\n%s\n\n%s' % (alert['description'], alert['instruction'], alert['areaDesc'])
        desc = re.sub(r'\s*\n\s*', ' ', re.sub(r'\s*\n\s*\n\s*', '\0',
                                               desc)).replace('\0', '\n\n').strip()
        if len(desc) > 250:
            desc = desc[:249] + '\u2026'
        text.append(desc)
        text.append('')
        text.append('')
    return '\n'.join(text).strip()
