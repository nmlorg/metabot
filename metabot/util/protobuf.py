"""Super-simple implementation of https://developers.google.com/protocol-buffers/docs/encoding."""

import functools


class ProtoBuf:
    """Base class for all protobuf files and nested fields."""

    _fields = ()

    def __init__(self, data=None):
        self._setters = {}
        for number, name, subtype, *desc in self._fields:
            if subtype is str:
                decoder = lambda data: bytes(data).decode('utf8')
            elif issubclass(subtype, ProtoBuf):
                decoder = functools.partial(lambda subtype, data: subtype(data), subtype)
            else:
                decoder = lambda data: data
            if desc and desc[0] is list:
                setattr(self, name, [])
                setter = functools.partial(
                    lambda name, decoder, data: getattr(self, name).append(decoder(data)), name,
                    decoder)
            else:
                setattr(self, name, None)
                setter = functools.partial(
                    lambda name, decoder, data: setattr(self, name, decoder(data)), name, decoder)
            self._setters[number] = setter

        if data is not None:
            self.merge_from_bytes(data)

    def merge_from_bytes(self, data):
        """Decode data, an iterable of ints, adding encoded values to self."""

        while data:
            field_type, value = get_field(data)
            if field_type is None:
                break
            if field_type in self._setters:
                self._setters[field_type](value)

    def __iter__(self):
        for _, name, *_ in self._fields:
            yield getattr(self, name)


def get_varint(data):
    """Decode a simple varint."""

    val = exp = 0
    while data:
        chunk = data.pop(0)
        val += (chunk & 0x7f) << (7 * exp)
        if not chunk & 0x80:
            break
        exp += 1
    return val


def get_field(data):
    """Decode a type/length/value tuple."""

    key = get_varint(data)
    wire_type, field_number = key & 0x7, key >> 3
    if wire_type == 0:
        return field_number, get_varint(data)
    if wire_type == 2:
        field_len = get_varint(data)
        value = data[:field_len]
        for _ in range(field_len):
            data.pop(0)
        return field_number, value
    return None, key
