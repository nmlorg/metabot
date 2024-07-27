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

PERIOD = 60 * 10  # Run modinit.periodic every 10 minutes.
PLAIN_TEXT_LIMIT = 4096
PHOTO_TEXT_LIMIT = 1024


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
            botuser, unused_groupid = key
            if botuser != 'alerts' and len(record) == 3:
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

    def __init__(self, groupconf):
        (self.calcodes, self.tzinfo, self.count, self.days, self.hour,
         self.dow) = eventutil.get_group_conf(groupconf)
        self.preambles = groupconf['daily'].get('text', '').splitlines()

    def get_events(self, bot, eventtime, base):
        """Get (and format) events for the given time."""

        events, alerts = eventutil.get_group_events(bot, self.calcodes, self.tzinfo, self.count,
                                                    self.days, eventtime)
        if self.preambles:
            preamble = self.preambles[int(eventtime / (60 * 60 * 24)) % len(self.preambles)]
        else:
            preamble = ''
        text = _generate_preamble(preamble, events)
        if events:
            text = f'{text}\n\n{eventutil.format_events(bot, events, self.tzinfo, base=base)}'
        return events, alerts, text


def _daily_messages(multibot, records):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    now = time.time()
    # If running at 11:22:33.444, act as if we're running at exactly 11:20:00.000.
    period = int(now // PERIOD * PERIOD)
    startofhour = now // 3600

    for botuser, botconf in multibot.conf['bots'].items():  # pylint: disable=too-many-nested-blocks
        for groupid, groupconf in botconf['issue37']['moderator'].items():
            annconf = AnnouncementConf(groupconf)
            if not annconf.tzinfo or not isinstance(annconf.hour, int):
                continue

            nowdt = datetime.datetime.fromtimestamp(now, annconf.tzinfo)
            perioddt = datetime.datetime.fromtimestamp(period, annconf.tzinfo)
            key = (botuser, groupid)
            if key in records:
                eventtime, lastevents, lastmessage, lasttext, lastsuffix = records[key]
            else:
                eventtime = 0

            if perioddt.hour == annconf.hour and not annconf.dow & 1 << perioddt.weekday() and (
                    not eventtime or startofhour > eventtime // 3600):
                sendnew = True
                eventtime = period
            elif eventtime:
                sendnew = False
            else:
                continue

            # See https://github.com/nmlorg/metabot/issues/26.
            bot = ntelebot.bot.Bot(botconf['issue37']['telegram']['token'])
            bot.multibot = multibot
            bot._username = botuser  # pylint: disable=protected-access

            events, alerts, text = annconf.get_events(bot, eventtime, perioddt)
            _handle_alerts(bot, records, groupid, alerts)

            message = None

            if sendnew:
                if events:
                    url = eventutil.get_image(events[0], botconf)
                    message = reminder_send(bot, groupid, text, url)
                    suffix = ''
            else:
                edits = diff_events(multibot, annconf.tzinfo, perioddt, lastevents, events)  # pylint: disable=possibly-used-before-assignment

                suffix = lastsuffix  # pylint: disable=possibly-used-before-assignment
                if edits:
                    updtext = 'Updated:\n' + '\n'.join(edits)
                    try:
                        updmessage = bot.send_message(
                            chat_id=groupid,
                            reply_to_message_id=lastmessage['message_id'],  # pylint: disable=possibly-used-before-assignment
                            text=_truncate(updtext, PLAIN_TEXT_LIMIT),
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

                if text != lasttext or suffix != lastsuffix:  # pylint: disable=possibly-used-before-assignment
                    newtext = text
                    if suffix:
                        newtext = f'{newtext}\n\n[{suffix}]'
                    message = reminder_edit(bot, groupid, lastmessage['message_id'], newtext,
                                            lastmessage.get('caption'))

            if message:
                records[key] = (eventtime, [event.copy() for event in events], message, text,
                                suffix)


def reminder_send(bot, groupid, text, photo):
    """Send a message with the given photo + caption, falling back to plain text."""

    logging.info('Sending reminder to %s.', groupid)
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
                                text=_truncate(text, PLAIN_TEXT_LIMIT),
                                parse_mode='HTML',
                                disable_web_page_preview=True,
                                disable_notification=True)
    except ntelebot.errors.Error:
        logging.exception('While sending to %s:\n%s', groupid, text)


def reminder_edit(bot, groupid, message_id, text, isphoto):
    """Edit a photo caption/plain message."""

    logging.info('Editing reminder %s/%s.', groupid, message_id)
    try:
        if isphoto:
            return bot.edit_message_caption(chat_id=groupid,
                                            message_id=message_id,
                                            caption=_truncate(text, PHOTO_TEXT_LIMIT),
                                            parse_mode='HTML')

        return bot.edit_message_text(chat_id=groupid,
                                     message_id=message_id,
                                     text=_truncate(text, PLAIN_TEXT_LIMIT),
                                     parse_mode='HTML',
                                     disable_web_page_preview=True)
    except ntelebot.errors.Error:
        logging.exception('While editing %s in %s:\n%s', message_id, groupid, text)


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


def _diff_time(laststart, lastend, curstart, curend, tzinfo, base):  # pylint: disable=too-many-arguments,too-many-locals,too-many-return-statements
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
                                       text=_truncate(text, PLAIN_TEXT_LIMIT),
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
