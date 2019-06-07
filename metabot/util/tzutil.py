"""Quick wrapper around pytz's zone.tab file (see https://bugs.launchpad.net/pytz/+bug/1324972)."""

import collections
import re

import pytz


def _zone_tab():
    zonetype = collections.namedtuple('Zone', ('code', 'coordinates', 'zone', 'comment'))
    with pytz.open_resource('zone.tab') as fobj:
        for line in fobj:
            line = line.decode('UTF-8')
            if line.startswith('#'):
                continue
            pieces = line.rstrip().split(None, 3)
            code, coordinates, zone = pieces[:3]
            comment = len(pieces) == 4 and pieces[3] or ''
            if zone not in pytz.all_timezones_set:
                continue

            coordinates = _parse_iso6709(coordinates)
            if not coordinates:
                continue
            lat, lon = coordinates

            yield zonetype(code, (lat, lon), zone, comment)


ZONE_TAB = pytz.LazyList(_zone_tab())


def _parse_iso6709(iso6709):
    match = re.match('^([-+][0-9]+)([-+][0-9]+)$', iso6709)
    if not match:
        return
    return map(_parse_iso6709_coord, match.groups())


def _parse_iso6709_coord(coord):
    if len(coord) % 2:
        deg = float(coord[:3])
        coord = coord[3:]
    else:
        deg = float(coord[:4])
        coord = coord[4:]
    div = 60
    while coord:
        deg += float(coord[:2]) / div
        div *= 60
        coord = coord[2:]
    return deg
