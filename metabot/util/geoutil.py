"""Quick utilities for geocoding an address and looking up its weather forecast."""

import logging
import time
import urllib.parse

import googlemaps
import requests

from metabot.util import iso8601
from metabot.util import pickleutil

try:
    _CLIENT_KEY = next(open('config/google_maps_apikey')).strip()
except IOError:
    _CLIENT = None
else:
    _CLIENT = googlemaps.Client(key=_CLIENT_KEY)
_CACHEFILE = 'config/geoutil.pickle'
_CACHE = pickleutil.load(_CACHEFILE) or {}
_SHORTCACHE = {}


def _save():
    pickleutil.dump(_CACHEFILE, _CACHE)


def geocode(address):
    """Look up the given address in Google Maps."""

    if 'geocode' not in _CACHE:
        _CACHE['geocode'] = {}
    if address not in _CACHE['geocode']:
        _CACHE['geocode'][address] = _CLIENT.geocode(address)
        _save()
    return _CACHE['geocode'][address]


def _weatherfetch(url):
    url = urllib.parse.urljoin('https://api.weather.gov/', url)
    headers = {
        'user-agent': 'https://github.com/nmlorg/metabot',
    }
    logging.info('Fetching %r.', url)
    return requests.get(url, headers=headers).json()


def weatherpoint(lat, lon):
    """Map a latitude/longitude to a weather.gov gridpoint."""

    # https://weather-gov.github.io/api/general-faqs#how-do-i-get-a-forecast-for-a-location-from-the-api
    lat = ('%.4f' % lat).rstrip('0')
    lon = ('%.4f' % lon).rstrip('0')
    key = '%s,%s' % (lat, lon)

    if 'weatherpoint' not in _CACHE:
        _CACHE['weatherpoint'] = {}
    if key not in _CACHE['weatherpoint']:
        _CACHE['weatherpoint'][key] = _weatherfetch('points/' + key)
        _save()
    return _CACHE['weatherpoint'][key]


def hourlyforecast(lat, lon):
    """Retrieve the hourly forecast for the given latitude/longitude."""

    point = weatherpoint(lat, lon)
    if not point.get('properties'):
        return ()
    now = time.time()
    url = point['properties']['forecastHourly']
    last, ret = _SHORTCACHE.get(url) or (0, None)
    if last < now - 10 * 60:
        ret = _weatherfetch(url)['properties']['periods']
        _SHORTCACHE[url] = (now, ret)
    return ret


def lookup(address, now=None):
    """Retrieve the forecasted weather conditions for the given address as of the given time."""

    if _CLIENT is None:
        return
    if now is None:
        now = time.time()
    ret = {}
    geo = geocode(address)
    if not geo:
        return
    ret['lat'] = geo[0]['geometry']['location']['lat']
    ret['lon'] = geo[0]['geometry']['location']['lng']
    for period in hourlyforecast(ret['lat'], ret['lon']):
        start = iso8601.totimestamp(period['startTime'])
        end = iso8601.totimestamp(period['endTime'])
        if start <= now < end:
            ret['forecast'] = period
            break
    return ret
