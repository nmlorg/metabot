"""Return a Calendar object for the given calid, constructing it if necessary."""

import importlib
import logging

from metabot.util import pickleutil

CALENDAR_TYPES = {}
CALENDARS = {}


def get(calid):
    """Return a Calendar object for the given calid, constructing it if necessary."""

    cal = CALENDARS.get(calid)
    if not cal:
        proto = calid.split(':', 1)[0]
        calendar_type = CALENDAR_TYPES.get(proto)
        if not calendar_type:
            module = importlib.import_module('metabot.calendars.' + proto)

            # pylint: disable=used-before-assignment
            class _CachingCalendar(_CachingCalendarMixin, module.Calendar):
                pass

            CALENDAR_TYPES[proto] = calendar_type = _CachingCalendar
        CALENDARS[calid] = cal = calendar_type(calid)
    return cal


class _CachingCalendarMixin:
    _cache_dir = 'calendars'

    def __init__(self, calid):
        super().__init__(calid)
        self.__fname = '%s/%s.pickle' % (self._cache_dir, self.calcode)
        data = pickleutil.load(self.__fname)
        if data:
            self.__dict__.update(data)

    def __save(self):
        logging.info('Rewriting %r.', self.__fname)
        self.__dict__.update(pickleutil.dump(self.__fname, self.__dict__))

    def poll(self):  # pylint: disable=missing-docstring
        if super().poll():
            self.__save()
            return True

    def add(self, local):  # pylint: disable=missing-docstring
        ret = super().add(local)
        self.__save()
        return ret

    def remove(self, local_id):  # pylint: disable=missing-docstring
        ret = super().remove(local_id)
        self.__save()
        return ret

    def update(self, local_id, local):  # pylint: disable=missing-docstring
        ret = super().update(local_id, local)
        self.__save()
        return ret
