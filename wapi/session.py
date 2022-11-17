try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests
import json
import time
import warnings
from past.types import basestring
import configparser

from . import auth, curves, events, util
from .util import CurveException


RETRY_COUNT = 4    # Number of times to retry
RETRY_DELAY = 0.5  # Delay between retried calls, in seconds.
TIMEOUT = 300      # Default timeout for web calls, in seconds.
API_URLBASE = 'https://api.wattsight.com'
AUTH_URLBASE = 'https://auth.wattsight.com'


class ConfigException(Exception):
    pass


class MetadataException(Exception):
    pass


class Session(object):
    """ Establish a connection to Wattsight API

    Creates an object that holds the state which is needed when talking to the
    Wattsight data center. To establish a session, you have to provide
    suthentication information either directly by using a ```client_id` and
    ``client_secret`` or using a ``config_file`` .

    See https://api.wattsight.com/#documentation for information how to get
    your authentication data.

    Parameters
    ----------

    urlbase: url
        Location of Wattsight service
    config_file: path
        path to the config.ini file which contains your authentication
        information.
    client_id: str
        Your client ID
    client_secret:
        Your client secret.
    auth_urlbase: url
        Location of Wattsight authentication service
    timeout: float
        Timeout for REST calls, in seconds

    Returns
    -------
    session: :class:`wapi.session.Session` object

    """

    def __init__(self, urlbase=None, config_file=None, client_id=None, client_secret=None,
                 auth_urlbase=None, timeout=None, retry_update_auth=False):
        self.urlbase = API_URLBASE
        self.auth = None
        self.timeout = TIMEOUT
        self._session = requests.Session()
        self.retry_update_auth = retry_update_auth
        if config_file is not None:
            self.read_config_file(config_file)
        elif client_id is not None and client_secret is not None:
            self.configure(client_id, client_secret, auth_urlbase)
        if urlbase is not None:
            self.urlbase = urlbase
        if timeout is not None:
            self.timeout = timeout

    def read_config_file(self, config_file):
        """Set up according to configuration file with hosts and access details"""
        if self.auth is not None:
            raise ConfigException('Session configuration is already done')
        config = configparser.RawConfigParser()
        # Support being given a file-like object or a file path:
        if hasattr(config_file, 'read'):
            config.read_file(config_file)
        else:
            files_read = config.read(config_file)
            if not files_read:
                raise ConfigException('Configuration file with name {} '
                                      'was not found.'.format(config_file))
        urlbase = config.get('common', 'urlbase', fallback=None)
        if urlbase is not None:
            self.urlbase = urlbase
        auth_type = config.get('common', 'auth_type')
        if auth_type == 'OAuth':
            client_id = config.get(auth_type, 'id')
            client_secret = config.get(auth_type, 'secret')
            auth_urlbase = config.get(auth_type, 'auth_urlbase', fallback=AUTH_URLBASE)
            self.auth = auth.OAuth(self, client_id, client_secret, auth_urlbase)
        timeout = config.get('common', 'timeout', fallback=None)
        if timeout is not None:
            self.timeout = float(timeout)

    def configure(self, client_id, client_secret, auth_urlbase=None):
        """Programmatically set authentication parameters"""
        if self.auth is not None:
            raise ConfigException('Session configuration is already done')
        if auth_urlbase is None:
            auth_urlbase = AUTH_URLBASE
        self.auth = auth.OAuth(self, client_id, client_secret, auth_urlbase)

    def get_curve(self, id=None, name=None):
        """Getting a curve object

        Return a curve object of the correct type.  Name should be specified.
        While it is possible to get a curve by id, this is not guaranteed to be
        long-term stable and will be removed in future versions.

        Parameters
        ----------

        id: int
            curve id (deprecated)
        name: str
            curve name

        Returns
        -------
        curve object
            Curve objects, can be one of:
            :class:`~wapi.curves.TimeSeriesCurve`,
            :class:`~wapi.curves.TaggedCurve`,
            :class:`~wapi.curves.InstanceCurve`,
            :class:`~wapi.curves.TaggedInstanceCurve`.
        """
        if id is not None:
            warnings.warn("Looking up a curve by ID will be removed in the future.", FutureWarning, stacklevel=2)
        if id is None and name is None:
            raise MetadataException('No curve specified')

        if id is not None:
            arg = util.make_arg('id', id)
        else:
            arg = util.make_arg('name', name)
        response = self.data_request('GET', self.urlbase, '/api/curves/get?{}'.format(arg))
        return self.handle_single_curve_response(response)

    def search(self, query=None, id=None, name=None, commodity=None, category=None, area=None, station=None,
               source=None, scenario=None, unit=None, time_zone=None, version=None, frequency=None, data_type=None,
               curve_state=None, modified_since=None, only_accessible=None):
        """
        Search for a curve matching various metadata.

        This function searches for curves that matches the given search
        parameters and returns a list of 0 or more curve objects.
        A curve object can be a
        :class:`~wapi.curves.TimeSeriesCurve`,
        :class:`~wapi.curves.TaggedCurve`,
        :class:`~wapi.curves.InstanceCurve` or a
        :class:`~wapi.curves.TaggedInstanceCurve` object.

        The search will return those curves matching all supplied parameters
        (logical AND). For most parameters, a list of values may be supplied.
        The search will match any of these values (logical OR).  If a single
        value contains a string with comma-separated values, these will be
        treated as a list but will match with logical AND. (This only makes
        sense for parameters where a curve may have multiple values:
        area (border curves), category, source and scenario.)

        For more details, see the REST documentation.

        Parameters
        ----------

        query: str
            A query string used for a language-aware text search on both names
            and descriptions of the various attributes in the curve.

        id: int or lits of int
            search for one or more specific id's (deprecated)

        name: str or list of str
            search for one or more curve names, you can use the ``*`` as
            a wildcard for patter matching.

        commodity: str or list of str
            search for curves that match the given ``commodity`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_commodities`

        category: str or list of str
            search for curves that match the given ``category`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_categories`

        area: str or list of str
            search for curves that match the given ``area`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_areas`

        station: str or list of str
            search for curves that match the given ``station`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_stations`

        source: str or list of str
            search for curves that match the given ``source`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_sources`

        scenario: str or list of str
            search for curves that match the given ``scenario`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_scenarios`

        unit: str or list of str
            search for curves that match the given ``unit`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_units`

        time_zone: str or list of str
            search for curves that match the given ``time_zone`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_time_zones`

        version: str or list of str
            search for curves that match the given ``version`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_versions`

        frequency: str or list of str
            search for curves that match the given ``frequency`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_frequencies`

        data_type: str or list of str
            search for curves that match the given ``data_type`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_data_types`

        curve_state: str or list of str
            search for curves that match the given ``curve_state`` attribute.
            Get valid values for this attribute with
            :meth:`wapi.session.Session.get_curve_state`

        modified_since: datestring, pandas.Timestamp or datetime.datetime
            only return curves that where modified after given datetime.

        only_accessible: bool
            If True, only return curves you have (some) access to.

        Returns
        -------
        curves: list
            list of curve objects, can be one of:
            :class:`~wapi.curves.TimeSeriesCurve`,
            :class:`~wapi.curves.TaggedCurve`,
            :class:`~wapi.curves.InstanceCurve`,
            :class:`~wapi.curves.TaggedInstanceCurve`.
        """
        search_terms = {
            'query': query,
            'id': id,
            'name': name,
            'commodity': commodity,
            'category': category,
            'area': area,
            'station': station,
            'source': source,
            'scenario': scenario,
            'unit': unit,
            'time_zone': time_zone,
            'version': version,
            'frequency': frequency,
            'data_type': data_type,
            'curve_state': curve_state,
            'modified_since': modified_since,
            'only_accessible': only_accessible,
        }
        if id is not None:
            warnings.warn("Searching for curves by ID will be removed in the future.", FutureWarning, stacklevel=2)
        args = []
        astr = ''
        for key, val in search_terms.items():
            if val is None:
                continue
            args.append(util.make_arg(key, val))
        if len(args):
            astr = "?{}".format("&".join(args))
        # Now run the search, and try to produce a list of curves
        response = self.data_request('GET', self.urlbase, '/api/curves{}'.format(astr))
        return self.handle_multi_curve_response(response)

    def make_curve(self, id, curve_type):
        """Return a mostly uninitialized curve object of the correct type.
        This is generally a bad idea, use get_curve or search when possible."""
        if curve_type in self._curve_types:
            return self._curve_types[curve_type](id, None, self)
        raise CurveException('Bad curve type requested')

    def events(self, curve_list, start_time=None, timeout=None):
        """Get an event listener for a list of curves."""
        return events.EventListener(self, curve_list, start_time=start_time, timeout=timeout)

    _attributes = {'commodities', 'categories', 'areas', 'stations', 'sources', 'scenarios',
                   'units', 'time_zones', 'versions', 'frequencies', 'data_types',
                   'curve_states', 'curve_types', 'functions', 'filters'}

    def get_commodities(self):
        """
        Get valid values for the commodity attribute
        """
        return self.get_attribute('commodities')

    def get_categories(self):
        """
        Get valid values for the category attribute
        """
        return self.get_attribute('categories')

    def get_areas(self):
        """
        Get valid values for the area attribute
        """
        return self.get_attribute('areas')

    def get_stations(self):
        """
        Get valid values for the station attribute
        """
        return self.get_attribute('stations')

    def get_sources(self):
        """
        Get valid values for the source attribute
        """
        return self.get_attribute('sources')

    def get_scenarios(self):
        """
        Get valid values for the scenarios attribute
        """
        return self.get_attribute('scenarios')

    def get_units(self):
        """
        Get valid values for the unit attribute
        """
        return self.get_attribute('units')

    def get_time_zones(self):
        """
        Get valid values for the time zone attribute
        """
        return self.get_attribute('time_zones')

    def get_versions(self):
        """
        Get valid values for the version attribute
        """
        return self.get_attribute('versions')

    def get_frequencies(self):
        """
        Get valid values for the frequency attribute
        """
        return self.get_attribute('frequencies')

    def get_data_types(self):
        """
        Get valid values for the data_type attribute
        """
        return self.get_attribute('data_types')

    def get_curve_states(self):
        """
        Get valid values for the curve_state attribute
        """
        return self.get_attribute('curve_states')

    def get_curve_types(self):
        """
        Get valid values for the curve_type attribute
        """
        return self.get_attribute('curve_types')

    def get_functions(self):
        """
        Get valid values for the function attribute
        """
        return self.get_attribute('functions')

    def get_filters(self):
        """
        Get valid values for the filter attribute
        """
        return self.get_attribute('filters')

    def get_attribute(self, attribute):
        """Get valid values for an attribute."""
        if attribute not in self._attributes:
            raise MetadataException('Attribute {} is not valid'.format(attribute))
        response = self.data_request('GET', self.urlbase, '/api/{}'.format(attribute))
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return None
        raise MetadataException('Failed loading {}: {}'.format(attribute,
                                                               response.content.decode()))

    _curve_types = {
        util.TIME_SERIES:      curves.TimeSeriesCurve,
        util.TAGGED:           curves.TaggedCurve,
        util.INSTANCES:        curves.InstanceCurve,
        util.TAGGED_INSTANCES: curves.TaggedInstanceCurve,
    }

    _meta_keys = ('id', 'name', 'frequency', 'time_zone', 'curve_type')

    def _build_curve(self, metadata):
        for key in self._meta_keys:
            if key not in metadata:
                raise MetadataException('Mandatory key {} not found in metadata'.format(key))
        curve_id = int(metadata['id'])
        if metadata['curve_type'] in self._curve_types:
            c = self._curve_types[metadata['curve_type']](curve_id, metadata, self)
            return c
        raise CurveException('Unknown curve type ({})'.format(metadata['curve_type']))

    def _get_auth_header_with_retry(self, databytes, retries=RETRY_COUNT):
        try:
            self.auth.validate_auth()
            return self.auth.get_headers(databytes)
        except Exception as e:
            if retries <= 0:
                raise e
            if RETRY_DELAY > 0:
                time.sleep(RETRY_DELAY)
            return self._get_auth_header_with_retry(databytes, retries - 1)

    def _validate_auth(self, data, rawdata):
        headers = {}

        databytes = None
        if data is not None:
            headers['content-type'] = 'application/json'
            if isinstance(data, basestring):
                databytes = data.encode()
            else:
                databytes = json.dumps(data).encode()
        if data is None and rawdata is not None:
            databytes = rawdata
        if self.auth is not None:
            # Beta-feature: Only update auth with retry if explicitly requested
            if self.retry_update_auth:
                auth_header = self._get_auth_header_with_retry(databytes)
                headers.update(auth_header)
            else:
                self.auth.validate_auth()
                headers.update(self.auth.get_headers(databytes))
        
        return headers
    
    def send_data_request(self, req_type, urlbase, url, data=None, rawdata=None, headers=None, authval=None,
                     stream=False, retries=RETRY_COUNT):
        if not urlbase:
            urlbase = self.urlbase
        longurl = urljoin(urlbase, url)

        databytes = None
        if data is not None:
            if isinstance(data, basestring):
                databytes = data.encode()
            else:
                databytes = json.dumps(data).encode()
        if data is None and rawdata is not None:
            databytes = rawdata
        timeout = None
        try:
            res = self._session.request(method=req_type, url=longurl, data=databytes,
                                        headers=headers, auth=authval, stream=stream, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            timeout = e
            res = None
        if (timeout is not None or (500 <= res.status_code < 600) or res.status_code == 408) and retries > 0:
            if RETRY_DELAY > 0:
                time.sleep(RETRY_DELAY)
            return self.send_data_request(req_type, urlbase, url, data, rawdata, headers, authval, stream, retries-1)
        if timeout is not None:
            raise timeout
        return res

    def data_request(self, req_type, urlbase, url, data=None, rawdata=None, authval=None,
                     stream=False, retries=RETRY_COUNT):
        """Run a call to the backend, dealing with authentication etc."""
        headers = self._validate_auth(data, rawdata)
        res = self.send_data_request(req_type, urlbase, url, data, rawdata, headers, authval, stream, retries)
        return res

    def handle_single_curve_response(self, response):
        if not response.ok:
            raise MetadataException('Failed to load curve: {}'
                                    .format(response.content.decode()))
        metadata = response.json()
        return self._build_curve(metadata)

    def handle_multi_curve_response(self, response):
        if not response.ok:
            raise MetadataException('Curve search failed: {}'
                                    .format(response.content.decode()))
        metadata_list = response.json()

        result = []
        for metadata in metadata_list:
            result.append(self._build_curve(metadata))
        return result
