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
from metabot.util import icons
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


def _daily_messages(multibot, records):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    now = time.time()
    for botuser, botconf in multibot.conf['bots'].items():  # pylint: disable=too-many-nested-blocks
        for groupid, groupconf in botconf['issue37']['moderator'].items():
            calcodes, tzinfo, count, days, hour, dow = eventutil.get_group_conf(groupconf)
            if not tzinfo or not isinstance(hour, int):
                continue
            # See https://github.com/nmlorg/metabot/issues/26.
            bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
            bot.multibot = multibot
            form = lambda event: eventutil.format_event(bot, event, tzinfo, full=False)  # pylint: disable=cell-var-from-loop
            title = lambda event: '  \u2022 ' + event['summary']
            nowdt = datetime.datetime.fromtimestamp(now, tzinfo)
            key = (botuser, groupid)
            if nowdt.hour == hour and not dow & 1 << nowdt.weekday():
                events, alerts = eventutil.get_group_events(bot, calcodes, tzinfo, count, days, now)
                _handle_alerts(bot, records, groupid, alerts)
                if events:
                    preambles = groupconf['daily'].get('text', '').splitlines()
                    preamble = (preambles and preambles[nowdt.toordinal() % len(preambles)] or '')
                    text = _format_daily_message(preamble, list(map(form, events)))
                    url = icons.match(events[0]['summary']) or icons.match(events[0]['description'])
                    message = None
                    if url:
                        try:
                            message = bot.send_photo(chat_id=groupid,
                                                     photo=url,
                                                     caption=text,
                                                     parse_mode='HTML',
                                                     disable_notification=True)
                        except ntelebot.errors.Error:
                            logging.exception('Downgrading to plain text:')
                    if not message:
                        try:
                            message = bot.send_message(chat_id=groupid,
                                                       text=text,
                                                       parse_mode='HTML',
                                                       disable_web_page_preview=True,
                                                       disable_notification=True)
                        except ntelebot.errors.Error:
                            logging.exception('While sending to %s:\n%s', groupid, text)
                    if message:
                        records[key] = (now, [event.copy() for event in events], message)
            elif key in records:
                lastnow, lastevents, lastmessage = records[key]
                lastmap = {event['local_id']: event for event in lastevents}
                events, alerts = eventutil.get_group_events(bot, calcodes, tzinfo, count, days,
                                                            lastnow)
                _handle_alerts(bot, records, groupid, alerts)
                curmap = {event['local_id']: event for event in events}
                bothevents = events.copy()
                bothevents.extend(event for event in lastevents if event['local_id'] not in curmap)
                bothevents.sort(key=operator.itemgetter('start', 'end', 'summary', 'local_id'))
                edits = []
                for event in bothevents:
                    lastevent = lastmap.get(event['local_id'])
                    if not lastevent:
                        edits.append(title(event))
                        edits.append('    \u25e6 New event!')
                        continue
                    event = multibot.multical.get_event(event['local_id'])[1]
                    if not event:
                        edits.append(title(lastevent))
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
                        edits.append(title(event))
                        for left, right in pieces:
                            edits.append('    \u25e6 <i>%s</i> \u2192 <b>%s</b>' % (left, right))

                if not edits:
                    continue
                text = 'Updated:\n' + '\n'.join(edits)
                try:
                    message = bot.send_message(chat_id=groupid,
                                               reply_to_message_id=lastmessage['message_id'],
                                               text=text,
                                               parse_mode='HTML',
                                               disable_web_page_preview=True,
                                               disable_notification=True)
                except ntelebot.errors.Error:
                    logging.exception('While sending to %s:\n%s', groupid, text)
                    continue

                lastnowdt = datetime.datetime.fromtimestamp(lastnow, tzinfo)
                preambles = groupconf['daily'].get('text', '').splitlines()
                preamble = preambles and preambles[lastnowdt.toordinal() % len(preambles)] or ''
                updated = 'Updated ' + humanize.time(nowdt)
                groupidnum = int(groupid)
                if -1002147483647 <= groupidnum < -1000000000000:
                    updated = '<a href="https://t.me/c/%s/%s">%s</a>' % (
                        -1000000000000 - groupidnum, message['message_id'], updated)
                else:
                    updated = '%s (%s)' % (updated, message['message_id'])
                text = '%s\n\n[%s]' % (_format_daily_message(preamble, list(map(form,
                                                                                events))), updated)
                try:
                    if lastmessage.get('caption'):
                        message = bot.edit_message_caption(chat_id=groupid,
                                                           message_id=lastmessage['message_id'],
                                                           caption=text,
                                                           parse_mode='HTML')
                    else:
                        message = bot.edit_message_text(chat_id=groupid,
                                                        message_id=lastmessage['message_id'],
                                                        text=text,
                                                        parse_mode='HTML',
                                                        disable_web_page_preview=True)
                except ntelebot.errors.Error:
                    logging.exception('While sending to %s:\n%s', groupid, text)
                else:
                    records[key] = (lastnow, [event.copy() for event in events], message)


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
    logging.info(
        'Alerts:\n%s', '\n'.join(('%(id)s | %(messageType)s | %(severity)s | %(certainty)s '
                                  '| %(urgency)s | %(event)s | %(instruction)s') % alert
                                 for alert in alerts))
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
