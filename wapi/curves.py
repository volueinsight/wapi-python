from past.types import basestring

from . import util


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

    def __str__(self):
        if hasattr(self, 'curve_type'):
            curve_type = self.curve_type
        else:
            curve_type = 'UNKNOWN'
        if hasattr(self, 'name'):
            name = self.name
        else:
            name = str(self.id)
        return "{}({})".format(curve_type, name)

    def _add_from_to(self, args, first, last, prefix=''):
        if first is not None:
            args.append(util.make_arg('{}from'.format(prefix), first))
        if last is not None:
            args.append(util.make_arg('{}to'.format(prefix), last))

    def _add_functions(self, args, time_zone, filter, function, frequency, output_time_zone):
        if time_zone is not None:
            args.append(util.make_arg('time_zone', time_zone))
        if filter is not None:
            args.append(util.make_arg('filter', filter))
        if function is not None:
            args.append(util.make_arg('function', function))
        if frequency is not None:
            args.append(util.make_arg('frequency', frequency))
        if output_time_zone is not None:
            args.append(util.make_arg('output_time_zone', output_time_zone))

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

    def access(self):
        url = '/api/curves/{}/access'.format(self.id)
        return self._load_data(url, 'Failed to load curve access')


class TimeSeriesCurve(BaseCurve):
    def get_data(self, data_from=None, data_to=None, time_zone=None, filter=None,
                 function=None, frequency=None, output_time_zone=None):
        """ Getting data from Time Series curves

        A Time Series curves holds a single time series.
        This is used for actual values, backcasts, normals, etc. This function
        fetches data between two given timestamps. It also possible to process
        the curve directly in the API using filter and aggregation functions.
        This can be used with great effect to reduce the amount of data
        retrieved if the full set of details is not needed.
        All time series are returned in a :class:`wapi.util.TS` object.

        Parameters
        ----------

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in any of the following types (also valid without time):

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as ``data_from``.
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters`.

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions`.

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function. You can find the valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        Returns
        -------
        :class:`wapi.util.TS` object
        """

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
        """ Get list of available tags for this curve

        Returns
        -------
        list
            Returns a list of all available tags for a Tagged Instance curve.
        """
        url = '/api/series/tagged/{}/tags'.format(self.id)
        return self._load_data(url, 'Failed to fetch tags')

    def get_data(self, tag=None, data_from=None, data_to=None, time_zone=None, filter=None,
                 function=None, frequency=None, output_time_zone=None):
        """ Getting data from TAGGED curves

        A tagged curve holds a set of closely related time series, each
        identified by a tag. The most common use of tags is for ensemble
        weather data.

        This function fetches data for one or multiple given tags and returns
        a list of :class:`wapi.util.TS` objects.
        It also possible to process the curve directly in the API using filter
        and aggregation functions. This can be used with great effect to reduce
        the amount of data retrieved if the full set of details is not needed.
        All time series are returned in a :class:`wapi.util.TS` object.

        Parameters
        ----------

        tag: str or list, optional
            tag or tags to get get the data for. If omitted, the default
            tag is returned. If a list of multiple tags is given, the function
            will return a list with a :class:`wapi.util.TS` object for each tag.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in any of the following types (also valid without time):

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as ``data_from``.
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        unwrap = False
        if tag is None:
            args = []
            unwrap = True
        else:
            if isinstance(tag, basestring):
                unwrap = True
            args=[util.make_arg('tag', tag)]
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
                         issue_dates=None, issue_weekdays=None, issue_days=None, issue_months=None,
                         issue_times=None, with_data=False, data_from=None, data_to=None,
                         time_zone=None, filter=None, function=None, frequency=None,
                         output_time_zone=None, only_accessible=True, modified_since=None):
        """ Getting data from INSTANCE curves for multiple issue_dates

        An INSTANCE curve typically represents forecast,
        and contains a time series for each issue_date of the forecast.
        This function returns a list of time series for all available
        issue_dates (within a given period, if specified)
        as a a list of :class:`wapi.util.TS` objects.
        It also possible to process
        the curve directly in the API using filter and aggregation functions.
        This can be used with great effect to reduce the amount of data
        retrieved if the full set of details is not needed.
        By default this function returns the :class:`wapi.util.TS` objects
        without data, which can be change by setting the "with_data" argument
        to True.

        Parameters
        ----------

        issue_date_from: time-stamp, optional
            Limits the timerange to return all available issue_dates.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange to return for the latest available issue_date.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps to return :class:`wapi.util.TS` objects for.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        issue_weekdays: list of str, optional
            Filter issue_date on day of week.

        issue_days: list of int, optional
            Filter issue_date on day of month

        issue_months: list of str, optional
            Filter issue_date on month

        issue_times: list of str, optional
            Filter issue_date on time of day

        with_data: bool, optional
            If with_data is False, the returned  :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        modified_since: datestring, pandas.Timestamp or datetime.datetime
            only return instances that where modified after given datetime.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.append(util.make_arg('issue_date', issue_dates))
        if issue_weekdays is not None:
            args.append(util.make_arg('issue_weekday', issue_weekdays))
        if issue_days is not None:
            args.append(util.make_arg('issue_day', issue_days))
        if issue_months is not None:
            args.append(util.make_arg('issue_month', issue_months))
        if issue_times is not None:
            args.append(util.make_arg('issue_time', issue_times))
        if modified_since is not None:
            args.append(util.make_arg('modified_since', modified_since))
        astr = '&'.join(args)
        url = '/api/instances/{}?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        return [util.TS(input_dict=r, curve_type=util.INSTANCES) for r in result]

    def get_instance(self, issue_date, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        """ Getting data from INSTANCE curves for a specific issue_date

        An INSTANCE curve typically represents forecast,
        and contains a time series for each issue_date of the forecast.
        This function returns the time series for a specified issue_date
        as a :class:`wapi.util.TS` object. It also possible to process
        the curve directly in the API using filter and aggregation functions.
        This can be used with great effect to reduce the amount of data
        retrieved if the full set of details is not needed.

        Parameters
        ----------
        issue_date: time-stamp
            Time-stamp representing the issue date to get get data for.
            The timestamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        with_data: bool, optional
            If with_data is False, the returned  :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('issue_date', issue_date),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if with_data:
            self._add_from_to(args, data_from, data_to)
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
        """ Getting data from INSTANCE curves for the latest available issue_date

        An INSTANCE curve typically represents forecast,
        and contains a time series for each issue_date of the forecast.
        This function returns the time series for the latest available
        issue_date (within a given period, if specified)
        as a :class:`wapi.util.TS` object. It also possible to process
        the curve directly in the API using filter and aggregation functions.
        This can be used with great effect to reduce the amount of data
        retrieved if the full set of details is not needed.

        Parameters
        ----------

        issue_date_from: time-stamp, optional
            Limits the timerange to search for the latest available issue_date.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange to search for the latest available issue_date.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps in which to search for the latest available
            issue_date.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        with_data: bool, optional
            If with_data is False, the returned  :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.append(util.make_arg('issue_date', issue_dates))
        astr = '&'.join(args)
        url = '/api/instances/{}/latest?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load instance')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.INSTANCES)


class TaggedInstanceCurve(BaseCurve):
    def get_tags(self):
        """ Get list of available tags for this curve

        Returns
        -------
        list
            Returns a list of all available tags for a Tagged Instance curve.
        """
        url = '/api/instances/tagged/{}/tags'.format(self.id)
        return self._load_data(url, 'Failed to fetch tags')

    def search_instances(self, tags=None, issue_date_from=None, issue_date_to=None,
                         issue_dates=None, issue_weekdays=None, issue_days=None, issue_months=None,
                         issue_times=None, with_data=False, data_from=None, data_to=None,
                         time_zone=None, filter=None, function=None, frequency=None,
                         output_time_zone=None, only_accessible=True, modified_since=None):
        """ Getting data from TAGGED_INSTANCE curves for multiple issue_dates

        A TAGGED INSTANCE curve typically represents forecast that contain
        multiple time series for each issue_date of the forecast, which are
        assigned to so called tags. Each timeseries is therefore defined by a
        unique combination of issue_date and tag. Ensamble forecasts are a
        typical use case for TAGGED INSTANCE curves.

        This function returns a list of time series for all available
        issue_dates (within a given period, if specified) and tags (from a
        given list of tags, if specified) as a a list of :class:`wapi.util.TS`
        objects.

        It also possible to process the curve directly in the API using filter
        and aggregation functions. This can be used with great effect to reduce
        the amount of data retrieved if the full set of details is not needed.
        By default this function returns the :class:`wapi.util.TS` objects
        without data, which can be change by setting the "with_data" argument
        to True.

        Parameters
        ----------

        tags: str or list, optional
            tag or tags to consider. The function will only return objects with
            tags defined here. If None (default) is given, all available tags
            are considered.

        issue_date_from: time-stamp, optional
            Limits the timerange to return all available issue_dates.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange to return for the latest available issue_date.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps to return :class:`wapi.util.TS` objects for.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        issue_weekdays: list of str, optional
            Filter issue_date on day of week.

        issue_days: list of int, optional
            Filter issue_date on day of month

        issue_months: list of str, optional
            Filter issue_date on month

        issue_times: list of str, optional
            Filter issue_date on time of day

        with_data: bool, optional
            If with_data is False, the returned :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        modified_since: datestring, pandas.Timestamp or datetime.datetime
            only return instances that where modified after given datetime.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.append(util.make_arg('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.append(util.make_arg('issue_date', issue_dates))
        if issue_weekdays is not None:
            args.append(util.make_arg('issue_weekday', issue_weekdays))
        if issue_days is not None:
            args.append(util.make_arg('issue_day', issue_days))
        if issue_months is not None:
            args.append(util.make_arg('issue_month', issue_months))
        if issue_times is not None:
            args.append(util.make_arg('issue_time', issue_times))
        if modified_since is not None:
            args.append(util.make_arg('modified_since', modified_since))
        astr = '&'.join(args)
        url = '/api/instances/tagged/{}?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find tagged instances')
        if result is None:
            return result
        return [util.TS(input_dict=r, curve_type=util.TAGGED_INSTANCES) for r in result]

    def get_instance(self, issue_date, tag=None, with_data=True, data_from=None, data_to=None,
                     time_zone=None, filter=None, function=None, frequency=None,
                     output_time_zone=None, only_accessible=True):
        """ Getting data from TAGGED_INSTANCE curves for a specific issue_date

        A TAGGED INSTANCE curve typically represents forecast that contain
        multiple time series for each issue_date of the forecast, which are
        assigned to so called tags. Each timeseries is therefore defined by a
        unique combination of issue_date and tag. Ensamble forecasts are a
        typical use case for TAGGED INSTANCE curves.

        This function returns a time series for the combinations of a specified
        issue_date and all given tags as a lit of :class:`wapi.util.TS` objects.
        It also possible to process the curve directly in the API using filter
        and aggregation functions. This can be used with great effect to reduce
        the amount of data retrieved if the full set of details is not needed.

        Parameters
        ----------

        issue_date: time-stamp
            Time-stamp representing the issue date to get get data for.
            The timestamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        tag: str or list, optional
            tag or tags to get get the data for. If omitted, the default
            tag is returned. If a list of multiple tags is given, the function
            will return a list with a :class:`wapi.util.TS` object for each tag.

        with_data: bool, optional
            If with_data is False, the returned  :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        Returns
        -------
        :class:`wapi.util.TS` object
        """

        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('issue_date', issue_date),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        unwrap = False
        if tag is None:
            unwrap = True
        else:
            if isinstance(tag, basestring):
                unwrap = True
            args.append(util.make_arg('tag', tag))
        if with_data:
            self._add_from_to(args, data_from, data_to)
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
        """ Getting data from TAGGED INSTANCE curves for the latest issue_date

        A TAGGED INSTANCE curve typically represents forecasts that contain
        multiple time series for each issue_date of the forecast, which are
        assigned to so called tags. Each timeseries is therefore defined by a
        unique combination of issue_date and tag. Ensamble forecasts are a
        typical use case for TAGGED INSTANCE curves.

        This function returns the time series for ONE tag and the latest
        available issue_date (within a given period, if specified)
        as :class:`wapi.util.TS` objects. The tag to get the data for
        can be specified in the "tags" argument. If None (=all tags)
        or a list of tags is provided, only the timeseries for one of the tags
        (the first one found to have valid data) is returned. So it is
        recommended to specify ONE desired tag in "tags".

        It also possible to process
        the curve directly in the API using filter and aggregation functions.
        This can be used with great effect to reduce the amount of data
        retrieved if the full set of details is not needed.

        Parameters
        ----------
        tags: string or list, optional
            tag or list of tags to consider when returning the
            :class:`wapi.util.TS` object. The function returns a timeseries
            for ONE of the given tags. If you want get data for a specific tag,
            only specify one tag here (recommended!).

        issue_date_from: time-stamp, optional
            Limits the timerange to search for the latest available issue_date.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange to search for the latest available issue_date.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps in which to search for the latest available
            issue_date.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        with_data: bool, optional
            If with_data is False, the returned  :class:`wapi.util.TS` object
            only contains the attributes and meta data information but no
            data values.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be the first date with data
            available. If only the date (without time) is
            given, the time is assumed to be 00:00. The timestamp can be
            provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available.

        time_zone: str, optional
            Change curve time zone BEFORE performing an aggregation/split
            or applying a filter. If no aggregation/split or filter is applied,
            this will simply change the timezone of the curve. Note that if
            "output_time_zone" is given, this will define the timezone of the
            returned curve, since it is applied AFTER performing an
            aggregation/split or applying a filter and thus AFTER changing
            to given "time_zone" here.

            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_time_zones`.

        filter: str, optional
            only get a specific subset of the data.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_filters` :

        function: str, optional
            function used to aggregate or split data, must be used together
            with the ``frequency`` parameter.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_functions` :

        frequency: str, optional
            data will be aggregated or split to the requested frequency using
            the given function.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        output_time_zone: str, optional
            Change curve time zone AFTER performing an aggregation/split
            or applying a filter.

        only_accessible: bool, optional
            If TRUE, only return instances you have access to.

        Returns
        -------
        :class:`wapi.util.TS` object
        """

        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('only_accessible', '{}'.format(only_accessible).lower())]
        if tags is not None:
            args.append(util.make_arg('tag', tags))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        if with_data:
            self._add_from_to(args, data_from, data_to, prefix='data_')
            self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if issue_dates is not None:
            args.append(util.make_arg('issue_date', issue_dates))
        astr = '&'.join(args)
        url = '/api/instances/tagged/{}/latest?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to load tagged instance')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.TAGGED_INSTANCES)
