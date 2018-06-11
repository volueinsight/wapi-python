from . import util
import datetime
try:
    from urllib.parse import urljoin, quote_plus
except ImportError:
    from urlparse import urljoin
    from urllib import quote_plus
from builtins import str
from past.types import basestring


class BaseCurve:
    def __init__(self, id, metadata, session):
        self._metadata = metadata
        self._session = session
        self.time_zone = 'CET'
        if metadata is None:
            self.hasMetadata = False
        else:
            self.hasMetadata = True
            for key, val in metadata.items():
                setattr(self, key, val)
        self.id = id
        self.tz = util.parse_tz(self.time_zone)

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

    def _load_data(self, url, failmsg, urlbase=None):
        if urlbase is None:
            urlbase = self._session.urlbase
        response = self._session.data_request('GET', urlbase, url)
        self._last_response = response
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204 or response.status_code == 404:
            return None
        raise util.CurveException('{}: {} ({})'.format(failmsg, response.content, response.status_code))

    @staticmethod
    def _make_arg(key, value):
        if isinstance(value, datetime.date):
            tmp = value.isoformat()
        else:
            tmp = '{}'.format(value)
        v = quote_plus(tmp)
        return '{}={}'.format(key, v)

    @staticmethod
    def _flatten(key, data):
        if hasattr(data, '__iter__') and not isinstance(data, str):
            return [BaseCurve._make_arg(key, d) for d in data]
        return [BaseCurve._make_arg(key, data)]

    def access(self):
        url = '/api/curves/{}/access'.format(self.id)
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
        url = '/api/series/{}{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load curve data')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.TIME_SERIES)


class TaggedCurve(BaseCurve):
    def get_tags(self):
        url = '/api/series/tagged/{}/tags'.format(self.id)
        return self._load_data(url, 'Failed to fetch tags')

    def get_data(self, tag=None, data_from=None, data_to=None, time_zone=None, filter=None,
                 function=None, frequency=None, output_time_zone=None):
        unwrap = False
        if tag is None:
            args = []
        else:
            if isinstance(tag, basestring):
                unwrap = True
            args=self._flatten('tag', tag)
        self._add_from_to(args, data_from, data_to)
        self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = '/api/series/tagged/{}?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load tagged curve data')
        if result is None:
            return result
        res = [util.TS(input_dict=r, curve_type=util.TAGGED) for r in result]
        if unwrap and len(res) == 1:
            res = res[0]
        return res


class InstanceCurve(BaseCurve):
    def search_instances(self, issue_date_from=None, issue_date_to=None,
                         issue_dates=None, with_data=False, data_from=None, data_to=None,
                         time_zone=None, filter=None, function=None, frequency=None,
                         output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = '/api/instances/{}?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        return [util.TS(input_dict=r, curve_type=util.INSTANCES) for r in result]

    def get_instance(self, issue_date, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('issue_date', issue_date),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = '/api/instances/{}/get?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load instance')
        if result is None:
            return result
        return util.TS(input_dict=result, issue_date=issue_date, curve_type=util.INSTANCES)

    def get_latest(self, issue_date_from=None, issue_date_to=None, issue_dates=None,
                   with_data=True, data_from=None, data_to=None, time_zone=None, filter=None,
                   function=None, frequency=None, output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.extend(self._flatten('issue_date', issue_dates))
        astr = '&'.join(args)
        url = '/api/instances/{}/latest?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load instance')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.INSTANCES)


class TaggedInstanceCurve(BaseCurve):
    def get_tags(self):
        url = '/api/instances/tagged/{}/tags'.format(self.id)
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
        url = '/api/instances/tagged/{}?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find tagged instances')
        if result is None:
            return result
        return [util.TS(input_dict=r, curve_type=util.TAGGED_INSTANCES) for r in result]

    def get_instance(self, issue_date, tag=None, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        args=[self._make_arg('with_data', '{}'.format(with_data).lower()),
              self._make_arg('issue_date', issue_date),
              self._make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        unwrap = False
        if tag is not None:
            if isinstance(tag, basestring):
                unwrap = True
            args.extend(self._flatten('tag', tag))
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        astr = '&'.join(args)
        url = '/api/instances/tagged/{}/get?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load tagged instance')
        if result is None:
            return result
        res = [util.TS(input_dict=r, issue_date=issue_date, curve_type=util.TAGGED_INSTANCES) for r in result]
        if unwrap and len(res) == 1:
            res = res[0]
        return res

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
        url = '/api/instances/tagged/{}/latest?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load tagged instance')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.TAGGED_INSTANCES)
