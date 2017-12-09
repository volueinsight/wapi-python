import pytz
from . import util
import datetime
try:
    from urllib.parse import urljoin, quote_plus
except ImportError:
    from urlparse import urljoin
    from urllib import quote_plus
from builtins import str


class MetadataException(Exception):
    pass


class CurveException(Exception):
    pass


class BaseCurve:
    def __init__(self, id, metadata, session, scenarios=0):
        self._metadata = metadata
        self._session = session
        self.scenarios = scenarios
        if metadata is None:
            self.hasMetadata = False
        else:
            self.hasMetadata = True
            for key, val in metadata.items():
                setattr(self, key, val)
        self.id = id
        try:
            self.tz = pytz.timezone(self.time_zone)
        except:
            # TODO: Add our own time zones.
            self.tz = pytz.utc

    def _add_from_to(self, args, first, last, prefix=''):
        if first is not None:
            args.append(self._make_arg('{}from'.format(prefix), first))
        if last is not None:
            args.append(self._make_arg('{}to'.format(prefix), last))

    def _add_functions(self, args, time_zone, filter, function, frequency, output_time_zone):
        if time_zone is not None:
            args.append(self._make_arg('time_zone', time_zone))
        if filter is not None:
            args.append(self._make_arg('filter', filter))
        if function is not None:
            args.append(self._make_arg('function', function))
        if frequency is not None:
            args.append(self._make_arg('frequency', frequency))
        if output_time_zone is not None:
            args.append(self._make_arg('output_time_zone', output_time_zone))

    def _load_data(self, url, failmsg):
        response = self._session.data_request('GET', url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204 or response.status_code == 404:
            return None
        raise CurveException('{}: {} ({})'.format(failmsg, response.content, response.status_code))

    @staticmethod
    def _make_arg(key, value):
        if isinstance(value, datetime.date):
            tmp = value.isoformat()
        else:
            tmp = '{}'.format(value)
        v = quote_plus(tmp)
        return '{}={}'.format(key, v)

    def access(self):
        url = urljoin(self._session.host, '/api/curves/{}/access'.format(self.id))
        return self._load_data(url, 'Failed to load curve access')


class TimeSeriesCurve(BaseCurve):
    def get_data(self, data_from=None, data_to=None, time_zone=None, filter=None,
                 function=None, frequency=None, output_time_zone=None):
        args = []
        astr = ''
        self._add_from_to(args, data_from, data_to)
        self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if len(args) > 0:
            astr = '?{}'.format('&'.join(args))
        url = urljoin(self._session.host, '/api/series/{}{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load curve data')
        if result is None:
            return result
        return util.TS(result, scenarios=self.scenarios)


class TaggedCurve(BaseCurve):
    def get_tags(self):
        url = urljoin(self._session.host, '/api/tagged/{}/tags'.format(self.id))
        return self._load_data(url, 'Failed to fetch tags')

    def get_data(self, tag, data_from=None, data_to=None, time_zone=None, filter=None,
                 function=None, frequency=None, output_time_zone=None):
        args=[self._make_arg('tag', tag)]
        self._add_from_to(args, data_from, data_to)
        self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/tagged/{}?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load curve data')
        if result is None:
            return result
        return util.TS(result, scenarios=self.scenarios, tag=tag)


class InstanceCurve(BaseCurve):
    def get_tags(self):
        url = urljoin(self._session.host, '/api/instances/{}/tags'.format(self.id))
        return self._load_data(url, 'Failed to fetch tags')

    def search_instances(self, tags=None, issue_date_from=None, issue_date_to=None,
                         issue_dates=None, with_data=False, data_from=None, data_to=None,
                         time_zone=None, filter=None, function=None, frequency=None,
                         output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.extend(self._flatten('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/instances/{}?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        res = []
        for r in result:
            if 'points' in r:
                res.append(util.Instance(r, scenarios=self.scenarios))
            else:
                res.append(r)
        return res

    def get_instance(self, tag, issue_date, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('tag', tag),
              self._make_arg('issue_date', issue_date),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/instances/{}/get?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load instance')
        if result is None or 'points' not in result:
            return result
        return util.Instance(result, scenarios=self.scenarios)

    def get_latest(self, tags=None, issue_date_from=None, issue_date_to=None, issue_dates=None,
                   with_data=True, data_from=None, data_to=None, time_zone=None, filter=None,
                   function=None, frequency=None, output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.extend(self._flatten('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/instances/{}/latest?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load instance')
        if result is None or 'points' not in result:
            return result
        return util.Instance(result, scenarios=self.scenarios)

    @staticmethod
    def _flatten(key, data):
        if hasattr(data, '__iter__') and not isinstance(data, str):
            return [BaseCurve._make_arg(key, d) for d in data]
        return [BaseCurve._make_arg(key, data)]


class TaggedInstanceCurve(BaseCurve):
    def get_tags(self):
        url = urljoin(self._session.host, '/api/tagged_instances/{}/tags'.format(self.id))
        return self._load_data(url, 'Failed to fetch tags')

    def search_instances(self, tags=None, issue_date_from=None, issue_date_to=None,
                         issue_dates=None, with_data=False, data_from=None, data_to=None,
                         time_zone=None, filter=None, function=None, frequency=None,
                         output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.extend(self._flatten('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/tagged_instances/{}?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        res = []
        for r in result:
            if 'points' in r:
                res.append(util.Instance(r, scenarios=self.scenarios))
            else:
                res.append(r)
        return res

    def get_instance(self, tag, issue_date, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('tag', tag),
              self._make_arg('issue_date', issue_date),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/tagged_instances/{}/get?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load instance')
        if result is None or 'points' not in result:
            return result
        return util.Instance(result, scenarios=self.scenarios)

    def get_latest(self, tags=None, issue_date_from=None, issue_date_to=None, issue_dates=None,
                   with_data=True, data_from=None, data_to=None, time_zone=None, filter=None,
                   function=None, frequency=None, output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.extend(self._flatten('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = urljoin(self._session.host, '/api/tagged_instances/{}/latest?{}'.format(self.id, astr))
        result = self._load_data(url, 'Failed to load instance')
        if result is None or 'points' not in result:
            return result
        return util.Instance(result, scenarios=self.scenarios)

    @staticmethod
    def _flatten(key, data):
        if hasattr(data, '__iter__') and not isinstance(data, str):
            return [BaseCurve._make_arg(key, d) for d in data]
        return [BaseCurve._make_arg(key, data)]
