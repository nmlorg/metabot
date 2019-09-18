"""Interface to https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts."""

SUPERSCRIPTS = {
    ' ': '\u2006',
    '0': '\u2070',
    '1': '\u00b9',
    '2': '\u00b2',
    '3': '\u00b3',
    '4': '\u2074',
    '5': '\u2075',
    '6': '\u2076',
    '7': '\u2077',
    '8': '\u2078',
    '9': '\u2079',
    'a': '\u1d43',
    'b': '\u1d47',
    'c': '\u1d9c',
    'd': '\u1d48',
    'e': '\u1d49',
    'f': '\u1da0',
    'g': '\u1d4d',
    'h': '\u02b0',
    'i': '\u2071',
    'j': '\u02b2',
    'k': '\u1d4f',
    'l': '\u02e1',
    'm': '\u1d50',
    'n': '\u207f',
    'o': '\u1d52',
    'p': '\u1d56',
    'q': '\u1d4d',  # No superscript for 'q', so use 'g' instead.
    'r': '\u02b3',
    's': '\u02e2',
    't': '\u1d57',
    'u': '\u1d58',
    'v': '\u1d5b',
    'w': '\u02b7',
    'x': '\u02e3',
    'y': '\u02b8',
    'z': '\u1dbb',
}


def superscript(text):
    """Convert '13 days' to '¹³ ᵈᵃʸˢ', etc."""

    return ''.join(SUPERSCRIPTS.get(char, char) for char in text)
