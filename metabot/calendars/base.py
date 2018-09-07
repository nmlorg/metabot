"""Base calendar container."""

from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import logging


class Calendar(object):
    """Base calendar container."""

    caltype = 'base'
    last_update = None

    def __init__(self, calid):
        caltype, self.calpath = calid.split(':', 1)
        assert caltype == self.caltype
        self.calcode = self._hashid(calid)
        self.events = {}

    @staticmethod
    def _hashid(uid):
        return hashlib.sha1(uid.encode('ascii')).hexdigest()[:8]

    def _normalize(self, local):
        location = local.get('location') or ''
        if location in ('TBA', 'TBD', '(none)'):
            location = ''
        elif location:
            location = location.replace('\n', ', ')
        local_id = local.get('local_id') or '%s:%s' % (self.calcode, self._hashid(local['id']))

        return {
            'description': local.get('description') or '',
            'end': local['end'],
            'id': local['id'],
            'local_id': local_id,
            'location': location,
            'start': local['start'],
            'summary': local.get('summary') or '',
            'updated': local['updated'],
        }

    def _removed(self, proto_id):
        local_id = '%s:%s' % (self.calcode, self._hashid(proto_id))
        local = self.events.pop(local_id, None)
        if local:
            logging.info('Event %s (%s) was removed.', local['id'], local['summary'])
            return True

    def _updated(self, proto):
        local = self._normalize(self.event_proto_to_local(proto))
        oldlocal = self.events.get(local['local_id'])
        if not oldlocal:
            logging.info('Event %s (%s) added.', local['id'], local['summary'])
        elif oldlocal != local:
            logging.info('Event %s (%s) updated.', local['id'], local['summary'])
        else:
            return
        self.events[local['local_id']] = local
        if not self.last_update or self.last_update < local['updated']:
            self.last_update = local['updated']
        return True

    def add(self, local):
        """Add an event (in local format)."""

        newlocal = self._normalize(
            self.event_proto_to_local(self.proto_add(self.event_local_to_proto(local))))
        logging.info('Added event %s (%s).', newlocal['id'], newlocal['summary'])
        self.events[newlocal['local_id']] = newlocal
        if not self.last_update or self.last_update < newlocal['updated']:
            self.last_update = newlocal['updated']
        return newlocal

    def remove(self, local_id):
        """Remove an event (given as calcode:localcode)."""

        currentlocal = self.events.pop(local_id)
        self.proto_remove(currentlocal['id'])
        logging.info('Removed event %s (%s).', currentlocal['id'], currentlocal['summary'])

    def update(self, local_id, local):
        """Update an event (given as calcode:localcode, in local format)."""

        currentlocal = self.events[local_id]
        newlocal = self._normalize(
            self.event_proto_to_local(
                self.proto_update(currentlocal['id'], self.event_local_to_proto(local))))
        logging.info('Updated event %s (%s).', newlocal['id'], newlocal['summary'])
        self.events[newlocal['local_id']] = newlocal
        if not self.last_update or self.last_update < newlocal['updated']:
            self.last_update = newlocal['updated']
        return newlocal

    @staticmethod
    def poll():  # pragma: no cover
        """Check the data provider for updates."""

        raise NotImplementedError

    @staticmethod
    def event_proto_to_local(proto):  # pragma: no cover
        """Convert an event from native data provider format to standardized local format."""

        raise NotImplementedError

    @staticmethod
    def event_local_to_proto(local):  # pragma: no cover
        """Convert an event from standardized local format to native data provider format."""

        raise NotImplementedError

    @staticmethod
    def proto_add(proto):  # pragma: no cover
        """Ask the data provider to create an event."""

        raise NotImplementedError

    @staticmethod
    def proto_remove(proto_id):  # pragma: no cover
        """Ask the data provider to remove an event."""

        raise NotImplementedError

    @staticmethod
    def proto_update(proto_id, proto):  # pragma: no cover
        """Ask the data provider to update an event."""

        raise NotImplementedError
