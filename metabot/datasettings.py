"""Simple container for bot, group, and user configuration."""


class DataSettings:  # pylint: disable=too-few-public-methods
    """Simple container for bot, group, and user configuration."""

    def __init__(self, data, settings):
        self.data = _Container(data)
        self.settings = _Container(settings)


class _Container:

    def __init__(self, data):
        self._data = data

    def __getitem__(self, field):
        return self._data[field]

    def __getattr__(self, field):
        return self[field]

    def __setitem__(self, field, value):
        self._data[field] = value

    def __setattr__(self, field, value):
        if field.startswith('_'):
            return super().__setattr__(field, value)

        self[field] = value
