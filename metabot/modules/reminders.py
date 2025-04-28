"""Announce upcoming events once a day."""

import collections
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

PERIOD = 60 * 10  # Run modinit.periodic every 10 minutes.


def modinit(multibot):  # pylint: disable=missing-docstring

    def queue():
        now = time.time()
        nextrun = (now // PERIOD + 1) * PERIOD
        jitter = random.random() * 5
        multibot.loop.queue.putwhen(nextrun + jitter, periodic)

    if multibot.conf.confdir:
        recordsfname = multibot.conf.confdir + '/daily.pickle'
        records = pickleutil.load(recordsfname) or {}

        for key, record in records.items():
            if len(record) == 3:
                records[key] += ('', '')
    else:
        recordsfname = None
        records = {}

    def periodic():
        logging.info('Running periodic.')
        try:
            multibot.multical.poll()
            _daily_messages(multibot, records)
            if recordsfname:
                pickleutil.dump(recordsfname, records)
        finally:
            queue()

    queue()


class AnnouncementConf:  # pylint: disable=too-few-public-methods
    """A group's announcement configuration."""

    def __init__(self, calconf, dailyconf):
        self.calconf = calconf
        self.dow = dailyconf.get('dow', 0)
        self.hour = dailyconf.get('hour')
        self.pin = dailyconf.get('pin', 0)
        self.preambles = dailyconf.get('text', '').splitlines()

    def get_events(self, bot, eventtime, base, *, countdown=True):
        """Get (and format) events for the given time."""

        calconf = self.calconf
        events = calconf.get_events(bot, when=eventtime)
        if self.preambles:
            preamble = self.preambles[int(eventtime / (60 * 60 * 24)) % len(self.preambles)]
        else:
            preamble = ''
        text = _generate_preamble(preamble, events)
        if events:
            ev = eventutil.format_events(bot,
                                         events,
                                         calconf.tzinfo,
                                         base=base,
                                         countdown=countdown)
            text = f'{text}\n\n{ev}'
        return events, text


class Announcement(collections.namedtuple('Announcement', 'time events message text suffix')):
    """The most recent announcement."""


def _daily_messages(multibot, records):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    now = time.time()
    # If running at 11:22:33.444, act as if we're running at exactly 11:20:00.000.
    period = int(now // PERIOD * PERIOD)
    startofhour = now // 3600

    for botuser, botconf in multibot.conf['bots'].items():  # pylint: disable=too-many-nested-blocks
        for groupid, groupconf in botconf['issue37']['moderator'].items():
            calconf = eventutil.CalendarConf(groupconf)
            annconf = AnnouncementConf(calconf, groupconf['daily'])
            if not calconf.tzinfo or not isinstance(annconf.hour, int):
                continue

            nowdt = datetime.datetime.fromtimestamp(now, calconf.tzinfo)
            perioddt = datetime.datetime.fromtimestamp(period, calconf.tzinfo)
            key = (botuser, groupid)
            if key in records:
                last = Announcement(*records[key])
            else:
                last = None

            # See https://github.com/nmlorg/metabot/issues/26.
            bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
            bot.multibot = multibot
            bot._username = botuser  # pylint: disable=protected-access

            if perioddt.hour == annconf.hour and not annconf.dow & 1 << perioddt.weekday() and (
                    not last or startofhour > last.time // 3600):
                events, text = annconf.get_events(bot, period, perioddt)
                if events:
                    url = eventutil.get_image(events[0], botconf)
                    message = reminder_send(bot, groupid, text, url)
                    if message:
                        if annconf.pin:
                            try:
                                bot.pin_chat_message(chat_id=message['chat']['id'],
                                                     message_id=message['message_id'],
                                                     disable_notification=True)
                                message['pinned'] = True
                            except ntelebot.errors.Error:
                                logging.exception('While pinning %s/%s:', message['chat']['id'],
                                                  message['message_id'])

                        records[key] = (period, [event.copy() for event in events], message, text,
                                        '')

                        if last:
                            text = annconf.get_events(bot, last.time, perioddt, countdown=False)[1]
                            reminder_edit(bot, last.message, text)

                            if last.message.get('pinned'):
                                try:
                                    bot.unpin_chat_message(chat_id=last.message['chat']['id'],
                                                           message_id=last.message['message_id'])
                                except ntelebot.errors.Error:
                                    logging.exception('While unpinning %s/%s:',
                                                      last.message['chat']['id'],
                                                      last.message['message_id'])
                    continue

            if last:
                events, text = annconf.get_events(bot, last.time, perioddt)
                edits = diff_events(multibot, calconf.tzinfo, perioddt, last.events, events)

                suffix = last.suffix
                if edits:
                    updtext = 'Updated:\n' + '\n'.join(edits)
                    try:
                        updmessage = bot.send_message(
                            chat_id=groupid,
                            reply_to_message_id=last.message['message_id'],
                            text=_truncate(updtext, ntelebot.limits.message_text_length_max),
                            parse_mode='HTML',
                            disable_web_page_preview=True,
                            disable_notification=True)
                    except ntelebot.errors.Error:
                        logging.exception('While sending to %s:\n%s', groupid, updtext)
                    else:
                        suffix = 'Updated ' + humanize.time(nowdt)
                        groupidnum = int(groupid)
                        if -1002147483647 <= groupidnum < -1000000000000:
                            suffix = '<a href="https://t.me/c/%s/%s">%s</a>' % (
                                -1000000000000 - groupidnum, updmessage['message_id'], suffix)

                if text != last.text or suffix != last.suffix:
                    newtext = text
                    if suffix:
                        newtext = f'{newtext}\n\n[{suffix}]'
                    message = reminder_edit(bot, last.message, newtext)
                    if message:
                        records[key] = (last.time, [event.copy() for event in events], message,
                                        text, suffix)


def reminder_send(bot, groupid, text, photo):
    """Send a message with the given photo + caption, falling back to plain text."""

    base = {
        'chat_id': groupid,
        'disable_notification': True,
        'parse_mode': 'HTML',
    }

    logging.info('Sending reminder to %s.', groupid)
    try:
        if photo:
            try:
                return bot.send_photo(**base, photo=photo, caption=text)
            except ntelebot.errors.TooLong:  # See https://github.com/nmlorg/metabot/issues/76.
                logging.info('Downgrading to plain text.')

        return bot.send_message(**base,
                                text=_truncate(text, ntelebot.limits.message_text_length_max),
                                disable_web_page_preview=True)
    except ntelebot.errors.Error:
        logging.exception('While sending to %s:\n%s', groupid, text)


def reminder_edit(bot, lastmessage, text):
    """Edit a photo caption/plain message."""

    groupid = lastmessage['chat']['id']
    message_id = lastmessage['message_id']
    base = {
        'chat_id': groupid,
        'message_id': message_id,
        'parse_mode': 'HTML',
    }

    logging.info('Editing reminder %s/%s.', groupid, message_id)
    try:
        if lastmessage.get('caption'):
            truncated = _truncate(text, ntelebot.limits.message_caption_length_max)
            message = bot.edit_message_caption(**base, caption=truncated)
        else:
            truncated = _truncate(text, ntelebot.limits.message_text_length_max)
            message = bot.edit_message_text(**base, text=truncated, disable_web_page_preview=True)
        if lastmessage.get('pinned'):
            message['pinned'] = True
        return message
    except ntelebot.errors.Unmodified:
        logging.exception('While editing %s/%s:\n%s', groupid, message_id, text)
        return lastmessage  # See https://github.com/nmlorg/metabot/issues/108.
    except ntelebot.errors.Error:
        logging.exception('While editing %s/%s:\n%s', groupid, message_id, text)


def _truncate(rawtext, length):
    text = html.truncate(rawtext, length)
    if text != rawtext:
        logging.info('Truncated:\n- %r\n+ %r', rawtext, text)
    return text


def diff_events(multibot, tzinfo, base, lastevents, events):  # pylint: disable=too-many-locals
    """Return a list of differences between lastevents and events."""

    lastmap = {event['local_id']: event for event in lastevents}
    curmap = {event['local_id']: event for event in events}
    bothevents = events.copy()
    bothevents.extend(event for event in lastevents if event['local_id'] not in curmap)
    bothevents.sort(key=operator.itemgetter('start', 'end', 'summary', 'local_id'))
    edits = []
    for event in bothevents:
        title = html.escape(event['summary'])

        lastevent = lastmap.get(event['local_id'])
        if not lastevent:
            edits.append(f'\u2022 <b>{title}</b> was added.')
            continue

        # See https://github.com/nmlorg/metabot/issues/75.
        event = multibot.multical.get_event(event['local_id'])[1]
        if not event:
            edits.append(f'\u2022 <s>{title}</s> was removed.')
            continue

        mentioned_event = False
        pieces = []

        diff = _quick_diff(html.escape(lastevent['summary']), html.escape(event['summary']))
        if diff:
            pieces.append(f'<s>{diff[0]}</s> is now called <b>{diff[1]}</b>')
            mentioned_event = True

        diff = _diff_time(lastevent['start'], lastevent['end'], event['start'], event['end'],
                          tzinfo, base)
        if diff:
            pieces.append(diff)

        diff = _quick_diff(html.escape(lastevent['location'].split(',', 1)[0]),
                           html.escape(event['location'].split(',', 1)[0]))
        if diff:
            pieces.append(f'was moved from <s>{diff[0]}</s> to <b>{diff[1]}</b>')

        diff = _quick_diff(html.sanitize(lastevent['description'], strip=True),
                           html.sanitize(event['description'], strip=True))
        if diff:
            if pieces:
                prefix = 'its description'
            else:
                prefix = f'The description of <b>{title}</b>'
                mentioned_event = True
            pieces.append(f'{prefix} was changed from <s>{diff[0]}</s> to <b>{diff[1]}</b>')

        if pieces:
            text = humanize.list(pieces)
            if not mentioned_event:
                text = f'<b>{title}</b> {text}'
            edits.append(f'\u2022 {text}.')

    return edits


def _diff_time(laststart, lastend, curstart, curend, tzinfo, base):  # pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments,too-many-return-statements
    laststartdt = datetime.datetime.fromtimestamp(laststart, tzinfo)
    lastenddt = datetime.datetime.fromtimestamp(lastend, tzinfo)
    curstartdt = datetime.datetime.fromtimestamp(curstart, tzinfo)
    curenddt = datetime.datetime.fromtimestamp(curend, tzinfo)

    laststartstr = humanize.date(laststartdt, base=base)
    lastendstr = humanize.date(lastenddt, base=base)
    curstartstr = humanize.date(curstartdt, base=base)
    curendstr = humanize.date(curenddt, base=base)

    start_earlier = curstart < laststart
    start_later = curstart > laststart
    start_same = curstart == laststart
    end_earlier = curend < lastend
    end_later = curend > lastend
    end_same = curend == lastend
    duration_same = lastend - laststart == curend - curstart

    # pylint: disable=line-too-long
    if not start_same and not end_same and not duration_same:  # Everything changed.
        return f'now starts at <b>{curstartstr}</b> and ends at <b>{curendstr}</b> (was <s>{laststartstr} to {lastendstr}</s>)'
    if start_earlier:
        if duration_same:
            return f'was moved up to <b>{curstartstr}</b> (from <s>{laststartstr}</s>; same duration)'
        return f'is starting earlier at <b>{curstartstr}</b> (instead of <s>{laststartstr}</s>; same end)'
    if start_later:
        if duration_same:
            return f'was moved back to <b>{curstartstr}</b> (from <s>{laststartstr}</s>; same duration)'
        return f'is starting later at <b>{curstartstr}</b> (instead of <s>{laststartstr}</s>; same end)'
    if end_earlier:
        return f'was shortened to <b>{curendstr}</b> (instead of <s>{lastendstr}</s>)'
    if end_later:
        return f'was extended to <b>{curendstr}</b> (instead of <s>{lastendstr}</s>)'


def _quick_diff(left, right):
    left = re.sub(r'https?://\S+', '', left)
    left = re.sub(r'\s+', ' ', left).strip()
    right = re.sub(r'https?://\S+', '', right)
    right = re.sub(r'\s+', ' ', right).strip()
    if left == right:
        return
    if not left:
        left = '(empty)'
    if not right:
        right = '(empty)'
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


def _generate_preamble(preamble, events):
    if not events:
        return preamble or 'No upcoming events!'

    if preamble and preamble.endswith(':') and 'events' in preamble.lower():
        return preamble

    if len(events) == 1:
        text = "There's an event coming up:"
    elif len(events) == 2:
        text = 'There are a couple events coming up:'
    elif len(events) == 3:
        text = 'There are a few events coming up:'
    else:
        text = 'There are a bunch of events coming up:'
    if preamble:
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
    return text
