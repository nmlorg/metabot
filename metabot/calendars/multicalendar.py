"""A manager that blends multiple base.Calendar objects' events together."""

from __future__ import absolute_import, division, print_function, unicode_literals

import operator
import time

from metabot.calendars import loader

try:
    dict.itervalues
except AttributeError:

    def itervalues(obj):  # pylint: disable=missing-docstring
        return obj.values()
else:  # pragma: no cover

    def itervalues(obj):  # pylint: disable=missing-docstring
        return obj.itervalues()


class MultiCalendar(object):
    """A manager that blends multiple base.Calendar objects' events together."""

    _current_index = None

    def __init__(self):
        self.calendars = {}
        self.by_local_id = {}
        self.ordered = []

    def _rebuild(self):
        self.ordered.sort(key=operator.itemgetter('start', 'end', 'summary', 'local_id'))
        current_index = None
        by_local_id = {}
        now = time.time()
        for i, event in enumerate(self.ordered):
            by_local_id[event['local_id']] = i
            if current_index is None and event['end'] >= now:
                current_index = i
        self._current_index = current_index
        self.by_local_id = by_local_id

    @property
    def current_index(self):
        """The index into self.ordered of the current (earliest ongoing or next to begin) event."""

        if self._current_index is None:
            return
        now = time.time()
        while self.ordered[self._current_index]['end'] < now:
            if self._current_index == len(self.ordered) - 1:
                self._current_index = None
                break
            self._current_index += 1
        return self._current_index

    @property
    def current_local_id(self):
        """The local_id of the current event."""

        cur = self.current_index
        if cur is not None:
            return self.ordered[cur]['local_id']

    def add(self, calid):
        """Add a new calendar to the manager (if it's not already installed)."""

        if calid not in self.calendars:
            self.calendars[calid] = loader.get(calid)
            self.ordered.extend(itervalues(self.calendars[calid].events))
            self._rebuild()
        return self.calendars[calid]

    def get_event(self, local_id=None):
        """Retrieve a specific event, plus the event immediately before and after it."""

        if local_id is None:
            index = self.current_index
        else:
            index = self.by_local_id.get(local_id)
        if index is None:
            return None, None, None
        prevev = nextev = None
        if index > 0:
            prevev = self.ordered[index - 1]
        if index < len(self.ordered) - 1:
            nextev = self.ordered[index + 1]
        return prevev, self.ordered[index], nextev

    def get_overlap(self, start, end):
        """Find all events whose [start, end] range overlaps the given [start, end] range."""

        for event in self.ordered:
            if event['start'] > end:
                break
            if event['end'] >= start:
                yield event

    def poll(self):
        """Poll all installed calendars for updates."""

        updated = False
        for calendar in itervalues(self.calendars):
            updated = calendar.poll() or updated
        if updated:
            self.ordered = []
            for calendar in itervalues(self.calendars):
                self.ordered.extend(itervalues(calendar.events))
            self._rebuild()
        return updated

    def view(self, calcodes):
        """A MultiCalendar-like object that operates on a subset of the installed calendars."""

        return View(self, calcodes)


class View(object):
    """A MultiCalendar-like object that operates on a subset of the installed calendars."""

    def __init__(self, multical, calcodes):
        self.multical = multical
        self.calcodes = calcodes

    @property
    def current_index(self):
        """The index into self.multical.ordered of the current event."""

        cur = self.multical.current_index
        if cur is None:
            return
        while self.multical.ordered[cur]['local_id'].split(':', 1)[0] not in self.calcodes:
            if cur == len(self.multical.ordered) - 1:
                return
            cur += 1
        return cur

    @property
    def current_local_id(self):
        """The local_id of the current event."""

        cur = self.current_index
        if cur is not None:
            return self.multical.ordered[cur]['local_id']

    def get_event(self, local_id=None):
        """Retrieve a specific event, plus the event immediately before and after it."""

        if local_id is None:
            index = self.current_index
        else:
            index = self.multical.by_local_id.get(local_id)
        if index is None:
            return None, None, None
        prevev = nextev = None

        previndex = index - 1
        while previndex >= 0:
            prevev = self.multical.ordered[previndex]
            if prevev['local_id'].split(':', 1)[0] in self.calcodes:
                break
            prevev = None
            previndex -= 1

        nextindex = index + 1
        while nextindex <= len(self.multical.ordered) - 1:
            nextev = self.multical.ordered[nextindex]
            if nextev['local_id'].split(':', 1)[0] in self.calcodes:
                break
            nextev = None
            nextindex += 1

        return prevev, self.multical.ordered[index], nextev

    def get_overlap(self, start, end):
        """Find all events whose [start, end] range overlaps the given [start, end] range."""

        for event in self.multical.get_overlap(start, end):
            if event['local_id'].split(':', 1)[0] in self.calcodes:
                yield event
