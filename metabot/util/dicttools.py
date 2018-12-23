"""A mutation-logging, key-implying dict (with accompanying list)."""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    unicode
except NameError:
    unicode = str  # pylint: disable=invalid-name,redefined-builtin


class ImplicitTrackingDict(dict):
    """A mutation-logging, key-implying dict."""

    def __init__(self, value=None, log=None, path=(), **kwargs):
        super(ImplicitTrackingDict, self).__init__(**kwargs)
        if log is not None:
            self.log = log
        else:
            self.log = {}
        self.path = path
        if value is not None:
            self.update(value)

    def finalize(self):
        """Trim empty hanging dicts, clear the audit log, and return a copy of the log."""

        self._trim()
        log = dict(self.log)
        self.log.clear()
        return log

    def _trim(self):
        for key, value in list(self.items()):
            if isinstance(value, ImplicitTrackingDict):
                value._trim()  # pylint: disable=protected-access
                if not value:
                    self.pop(key)

    def audit(self, path, value, current):
        """Record a mutation of root-path path from current to value."""

        if path not in self.log:
            self.log[path] = (value, current)
        else:
            orig = self.log[path][1]
            if value == orig:
                self.log.pop(path)
            else:
                self.log[path] = (value, orig)

    def clear(self):
        for key in list(self):
            self.pop(key)

    def pop(self, key, default=None):
        path = self.path + (key,)
        current = super(ImplicitTrackingDict, self).pop(key, None)
        if current is None:
            return default
        if isinstance(current, ImplicitTrackingDict):
            ret = dict(current)
            current.clear()
            current = ret
        else:
            self.audit(path, None, current)
        return current

    def update(self, values):
        for key, value in values.items():
            self[key] = value

    def __delitem__(self, key):
        self.pop(key)

    def __missing__(self, key):
        self[key] = {}
        return self[key]

    def __setitem__(self, key, value):
        if value is None:
            return self.__delitem__(key)

        current = self.get(key)
        if value == current:
            return
        if isinstance(current, ImplicitTrackingDict):
            current.clear()
            current = None

        path = self.path + (key,)
        if isinstance(value, dict):
            value = ImplicitTrackingDict(value=value, log=self.log, path=path)
        elif isinstance(value, (list, tuple)):
            value = TrackingList(value=value, log=self.log, path=path)
        elif isinstance(value, bytes):  # PyYAML converts ASCII strings to str in Python 2.7.
            value = value.decode('ascii')
        else:
            assert isinstance(value, (int, unicode)), repr(value)

        super(ImplicitTrackingDict, self).__setitem__(key, value)

        if not isinstance(value, (ImplicitTrackingDict, TrackingList)):
            self.audit(path, value, current)


class TrackingList(list):
    """A mutation-logging list."""

    def __init__(self, value=None, log=None, path=(), **kwargs):
        super(TrackingList, self).__init__(**kwargs)
        if log is not None:
            self.log = log
        else:
            self.log = {}  # pragma: no cover
        self.path = path
        if value is not None:
            self.extend(value)

    def audit(self, current):
        """Record a mutation of root-path self.path from current to self."""

        value = tuple(self)
        if self.path not in self.log:
            self.log[self.path] = (value, current)
        else:
            orig = self.log[self.path][1]
            if value == orig:
                self.log.pop(self.path)
            else:
                self.log[self.path] = (value, orig)

    def append(self, value):
        assert isinstance(value, (int, unicode)), value
        current = tuple(self)
        super(TrackingList, self).append(value)
        self.audit(current)

    def clear(self):  # pylint: disable=missing-docstring
        while self:
            self.pop()

    def extend(self, values):
        for value in values:
            self.append(value)

    def insert(self, index, value):
        assert isinstance(value, (int, unicode)), value
        current = tuple(self)
        super(TrackingList, self).insert(index, value)
        self.audit(current)

    def pop(self, index=-1):
        current = tuple(self)
        ret = super(TrackingList, self).pop(index)
        self.audit(current)
        return ret

    def remove(self, value):
        current = tuple(self)
        super(TrackingList, self).remove(value)
        self.audit(current)

    def reverse(self):
        current = tuple(self)
        super(TrackingList, self).reverse()
        self.audit(current)

    def sort(self, **kwargs):
        current = tuple(self)
        super(TrackingList, self).sort(**kwargs)
        self.audit(current)

    def __setitem__(self, index, value):
        assert isinstance(value, (int, unicode)), value
        if self[index] == value:
            return
        current = tuple(self)
        super(TrackingList, self).__setitem__(index, value)
        self.audit(current)
