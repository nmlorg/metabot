"""Helper to map Manager.xxx <-> BotConf[...][xxx]."""

import typing


class Field:
    """Helper to map Manager.xxx <-> BotConf[...][xxx]."""

    def __init__(self, container, key, _type):
        if callable(container):
            getcontainer = container
        else:
            getcontainer = lambda self: container
        self.getcontainer = getcontainer

        if callable(key):
            getkey = key
        else:
            getkey = lambda self: key
        self.getkey = getkey

        assert isinstance(_type, type)
        self.type = _type

        if issubclass(_type, typing.Collection):
            getdefault = _type
        else:
            getdefault = None
        self.getdefault = getdefault

    name = '<attribute>'

    def __set_name__(self, owner, name):
        self.name = f'{owner.__module__}.{owner.__name__}.{name}'

    def __get__(self, obj, objtype=None):
        container = self.getcontainer(obj)
        key = self.getkey(obj)

        if isinstance(container, dict):
            value = container.get(key, Field)
        elif isinstance(container, list):
            value = key in container
        else:
            value = getattr(container, key, Field)

        if value is not Field:
            return value

        if self.getdefault:
            self.__set__(obj, self.getdefault())
            return self.__get__(obj, objtype=objtype)

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, self.type):
            raise TypeError(f'Setting {self.name} ({self.type.__name__}) = {value!r}')

        container = self.getcontainer(obj)
        key = self.getkey(obj)

        if isinstance(container, dict):
            container[key] = value
        elif isinstance(container, list):
            value = bool(value)
            if value != (key in container):
                if value:
                    container.append(key)
                    container.sort()
                else:
                    container.remove(key)
        else:
            setattr(container, key, value)
