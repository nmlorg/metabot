"""Tests for metabot.util.protobuf."""

from metabot.util import protobuf


def test_get_varint():
    """Test basic behavior of get_varint."""

    # https://developers.google.com/protocol-buffers/docs/encoding#varints
    data = [0b00000001]
    assert (protobuf.get_varint(data), data) == (1, [])

    data = [0b10101100, 0b00000010]
    assert (protobuf.get_varint(data), data) == (300, [])


def test_get_field():
    """Test basic behavior of get_field."""

    # https://developers.google.com/protocol-buffers/docs/encoding#simple
    data = [0x08, 0x96, 0x01]
    assert (protobuf.get_field(data), data) == ((1, 150), [])

    # https://developers.google.com/protocol-buffers/docs/encoding#strings
    data = [0x12, 0x07, 0x74, 0x65, 0x73, 0x74, 0x69, 0x6e, 0x67]
    assert (protobuf.get_field(data), data) == ((2, list(b'testing')), [])


class PBTest1(protobuf.ProtoBuf):  # pylint: disable=missing-docstring,too-few-public-methods
    # https://developers.google.com/protocol-buffers/docs/encoding#simple
    _fields = ((1, 'a', int),)


class PBTest2(protobuf.ProtoBuf):  # pylint: disable=missing-docstring,too-few-public-methods
    # https://developers.google.com/protocol-buffers/docs/encoding#strings
    _fields = ((2, 'b', str),)


class PBTest3(protobuf.ProtoBuf):  # pylint: disable=missing-docstring,too-few-public-methods
    # https://developers.google.com/protocol-buffers/docs/encoding#embedded
    _fields = ((3, 'c', PBTest1),)


def test_protobuf():
    """Test basic behavior of ProtoBuf."""

    pbuf = PBTest3([0x1a, 0x03, 0x08, 0x96, 0x01])
    assert isinstance(pbuf.c, PBTest1)  # pylint: disable=no-member
    assert pbuf.c.a == 150  # pylint: disable=no-member

    pbuf = PBTest2([0x12, 0x07, 0x74, 0x65, 0x73, 0x74, 0x69, 0x6e, 0x67])
    assert pbuf.b == 'testing'  # pylint: disable=no-member
