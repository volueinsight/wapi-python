
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from builtins import str

import requests

from . import auth, curves, events


class ConfigException(Exception):
    pass


class MetadataException(Exception):
    pass


class CurveException(Exception):
    pass


# Curve types
TIME_SERIES = 'TIME_SERIES'
TAGGED = 'TAGGED'
INSTANCES = 'INSTANCES'
TAGGED_INSTANCES = 'TAGGED_INSTANCES'


class Session(object):
    """
    Class to hold the state which is needed when talking to the Wattsight data center,
    e.g. configuration, access keys, sockets for long-running requests etc.
    """

    def __init__(self, host=None, config_file=None):
        self.host = 'https://data.wattsight.com'
        self.auth = None
        self._curve_cache = {}
        self._name_cache = {}
        self._session = requests.Session()
        if config_file is not None:
            self.configure(config_file)
        if host is not None:
            self.host = host

    def configure(self, config_file):
        """Set up according to configuration file with hosts and access details"""
        if self.auth is not None:
            raise ConfigException('Session configuration is already done')
        config = configparser.RawConfigParser({"common": {"host": self.host}})
        # Support being given a file-like object or a file path:
        if hasattr(config_file, 'read'):
            config.read_file(config_file)
        else:
            config.read(config_file)
        host = config.get('common', 'host')
        if host is not None:
            self.host = host
        auth_type = config.get('common', 'auth_type')
        if auth_type == 'OAuth':
            client_id = config.get(auth_type, 'id')
            client_secret = config.get(auth_type, 'secret')
            auth_host = config.get(auth_type, 'auth_host')
            self.auth = auth.OAuth(self, client_id, client_secret, auth_host)

    def get_curve(self, id=None, name=None):
        """Return a curve object of the correct type.  Either id or name must be specified."""
        if id is None and name is None:
            raise MetadataException('No curve specified')
        if id is None:
            if name in self._name_cache:
                id = self._name_cache[name]
        if id in self._curve_cache:
            return self._curve_cache[id]

        if id is not None:
            arg = 'id={}'.format(id)
        else:
            arg = 'name={}'.format(name)
        url = urljoin(self.host, '/api/curves/get?{}'.format(arg))
        response = self.data_request('GET', url)
        if not response.ok:
            raise MetadataException("Failed to load curve: {}".format(response.content.decode()))
        metadata = response.json()
        return self._build_curve(metadata)

    _search_terms = ['query', 'id', 'area', 'category', 'commodity', 'data_type', 'frequency',
                     'source', 'station', 'time_zone', 'curve_state', 'unit', 'name']

    def search(self, **kwargs):
        """Search for a curve."""
        # First establish query from keyword args
        args = []
        astr = ''
        for key, val in kwargs.items():
            if key not in self._search_terms:
                raise MetadataException("Illegal search parameter {}".format(key))
            if hasattr(val, '__iter__') and not isinstance(val, str):
                args.extend(['{}={}'.format(key, v) for v in val])
            else:
                args.append('{}={}'.format(key, val))
        if len(args):
            astr = "?{}".format("&".join(args))
        url = urljoin(self.host, "/api/curves{}".format(astr))
        # Now run the search, and try to produce a list of curves
        response = self.data_request('GET', url)
        if not response.ok:
            raise MetadataException("Curve search failed: {}".format(response.content.decode()))
        metadata_list = response.json()

        result = []
        for metadata in metadata_list:
            result.append(self._build_curve(metadata))
        return result

    def make_curve(self, id, curve_type):
        """Return a mostly uninitialized curve object of the correct type.
        This is generally a bad idea, use get_curve or search when possible."""
        if curve_type in self._curve_types:
            return self._curve_types[curve_type](id, None, self)
        raise CurveException('Bad curve type requested')

    def events(self, curve_list, start_time=None, timeout=None):
        """Get an even listener for a list of curves."""
        return events.EventListener(self, curve_list, start_time=start_time, timeout=timeout)

    _attributes = {'areas', 'categories', 'commodities', 'curve_types', 'data_types',
                   'frequencies', 'sources', 'stations',
                   'curve_states', 'time_zones', 'units'}

    def get_attribute(self, attribute):
        """Get valid values for an attribute."""
        if attribute not in self._attributes:
            raise MetadataException('Attribute {} is not valid'.format(attribute))
        url = urljoin(self.host, '/api/{}'.format(attribute))
        response = self.data_request('GET', url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return None
        raise MetadataException('Failed loading {}: {}'.format(attribute,
                                                               response.content.decode()))

    _curve_types = {
        TIME_SERIES:      curves.TimeSeriesCurve,
        TAGGED:           curves.TaggedCurve,
        INSTANCES:        curves.InstanceCurve,
        TAGGED_INSTANCES: curves.TaggedInstanceCurve,
    }

    _meta_keys = ('id', 'name', 'frequency', 'time_zone', 'curve_type')

    def _build_curve(self, metadata):
        for key in self._meta_keys:
            if key not in metadata:
                raise MetadataException('Mandatory key {} not found in metadata'.format(key))
        curve_id = int(metadata['id'])
        if metadata['curve_type'] in self._curve_types:
            c = self._curve_types[metadata['curve_type']](curve_id, metadata, self)
            self._curve_cache[curve_id] = c
            self._name_cache[c.name] = curve_id
            return c
        raise CurveException('Unknown curve type ({})'.format(metadata['curve_type']))

    def data_request(self, req_type, url, data=None, authval=None):
        """Run a call to the backend, dealing with signatures etc."""
        headers = {}
        if self.auth is not None:
            self.auth.validate_auth()
            headers.update(self.auth.get_headers(data))
        if data is not None:
            headers['content_type'] = 'application/json'
            if isinstance(data, str):
                data = data.encode()
        req = requests.Request(method=req_type, url=url, data=data, headers=headers, auth=authval)
        prepared = self._session.prepare_request(req)
        return self._session.send(prepared)
