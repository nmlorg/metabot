"""Simple static calendar for use in tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

from metabot.calendars import base


class Calendar(base.Calendar):
    """Simple static calendar for use in tests."""

    caltype = 'static'
    __last_id = 0
    __last_update = 0
    poll_result = False

    def __init__(self, calid):
        super(Calendar, self).__init__(calid)
        self.__live_events = {}

    def poll(self):
        return self.poll_result

    @staticmethod
    def event_proto_to_local(proto):
        return {key.lower(): value for key, value in proto.items()}

    @staticmethod
    def event_local_to_proto(local):
        return {key.upper(): value for key, value in local.items()}

    def proto_add(self, proto):
        newproto = dict(proto)
        self.__last_id += 1
        newproto['ID'] = '%s' % self.__last_id
        self.__last_update += 1
        newproto['UPDATED'] = 1000 + self.__last_update
        self.__live_events[newproto['ID']] = newproto
        return newproto

    def proto_update(self, proto_id, proto):
        current = self.__live_events[proto_id]
        current.update(proto)
        self.__last_update += 1
        current['UPDATED'] = 1000 + self.__last_update
        return current

    def proto_remove(self, proto_id):
        self.__live_events.pop(proto_id)
