"""Quick utilities for geocoding an address and looking up its weather forecast."""

import logging
import threading
import time
import urllib.parse

import googlemaps
import ntelebot

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
_SHORTCACHE_AGE = 60 * 9.5
_PREFETCH_AGE = 60 * 60 * 24 * 2


def _periodic():
    while True:
        request_cutoff = time.time() - _PREFETCH_AGE
        candidates = sorted((last_check, url)
                            for url, (last_request, last_check, forecast) in _SHORTCACHE.items()
                            if last_request >= request_cutoff)
        delay = 60
        if candidates:
            _cachedfetch(candidates[0][1], live=False)
            delay = max(5, _SHORTCACHE_AGE / len(candidates))
        time.sleep(delay)


def _init():
    thr = threading.Thread(target=_periodic)
    thr.daemon = True
    thr.start()


_init()


def _cachedfetch(url, *, live=True):
    now = time.time()
    last_request, last_check, forecast = _SHORTCACHE.get(url) or (0, 0, None)
    if live:
        last_request = now
    elif last_check <= now - _SHORTCACHE_AGE:
        try:
            forecast = _weatherfetch(url)
        except (ntelebot.requests.ConnectionError, ntelebot.requests.ReadTimeout):
            logging.info('Timeout fetching %r.', url)
        except Exception:  # pylint: disable=broad-except
            logging.exception('While fetching %r:', url)
        else:
            last_check = now
    _SHORTCACHE[url] = (last_request, last_check, forecast)
    return forecast


def _save():
    pickleutil.dump(_CACHEFILE, _CACHE)


def _geocode(address):
    """Look up the given address in Google Maps."""

    if _CLIENT is None:
        return
    if 'geocode' not in _CACHE:
        _CACHE['geocode'] = {}
    if address not in _CACHE['geocode']:
        logging.info('Geocoding %r.', address)
        _CACHE['geocode'][address] = _CLIENT.geocode(address)
        _save()
    return _CACHE['geocode'][address]


def _weatherfetch(url):
    url = urllib.parse.urljoin('https://api.weather.gov/', url)
    headers = {
        'user-agent': 'https://github.com/nmlorg/metabot',
    }
    return ntelebot.requests.get(url, headers=headers, timeout=10).json()


def _weatherpoint(lat, lon):
    """Map a latitude/longitude to a weather.gov gridpoint."""

    # https://weather-gov.github.io/api/general-faqs#how-do-i-get-a-forecast-for-a-location-from-the-api
    lat = ('%.4f' % lat).rstrip('0')
    lon = ('%.4f' % lon).rstrip('0')
    key = '%s,%s' % (lat, lon)

    if 'weatherpoint' not in _CACHE:
        _CACHE['weatherpoint'] = {}
    if key not in _CACHE['weatherpoint']:
        try:
            _CACHE['weatherpoint'][key] = _weatherfetch('points/' + key)
        except (ntelebot.requests.ConnectionError, ntelebot.requests.ReadTimeout):
            logging.exception('Timeout looking up point %r.', key)
        except Exception:  # pylint: disable=broad-except
            logging.exception('While looking up point %r:', key)
        else:
            _save()
    return _CACHE['weatherpoint'].get(key)


def hourlyforecast(address, when):
    """Retrieve the hourly forecast for the given address."""

    if not (geo := _geocode(address)):
        return
    lat = geo[0]['geometry']['location']['lat']
    lon = geo[0]['geometry']['location']['lng']

    if not (point := _weatherpoint(lat, lon)):
        return
    url = point['properties']['forecastHourly']

    if not (forecasts := _cachedfetch(url)):
        return

    for period in forecasts['properties']['periods']:
        start = iso8601.totimestamp(period['startTime'])
        end = iso8601.totimestamp(period['endTime'])
        if start <= when < end:
            return period
