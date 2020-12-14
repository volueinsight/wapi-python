from past.types import basestring
import warnings

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
            tag or tags to get the data for. If omitted, the default
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
                         output_time_zone=None, only_accessible=None, modified_since=None):
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
            Format is 'HH', 'HH:mm' or 'HH:mm:ss'.

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

        modified_since: datestring, pandas.Timestamp or datetime.datetime
            only return instances that where modified after given datetime.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower())]
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
                     output_time_zone=None, only_accessible=None):
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
            Time-stamp representing the issue date to get data for.
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

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('issue_date', issue_date)]
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
                   function=None, frequency=None, output_time_zone=None, only_accessible=None):
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

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower())]
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

    def get_relative(self, data_offset, data_max_length=None, issue_date_from=None, issue_date_to=None,
                     issue_dates=None, issue_weekdays=None, issue_days=None, issue_months=None, issue_times=None,
                     data_from=None, data_to=None, time_zone=None, filter=None, function=None,
                     frequency=None, output_time_zone=None):
        """ Get a relative forecast from the INSTANCE curve

        A relative forecast is a time series created by joining multiple
        instances so that the data date is issue_date + data_offset.
        If the data frequency is higher than the frequency of the selected
        instances, a range of data values from each instance will be used.
        Similarly if the issue frequency is higher than the data frequency,
        the same data date will be used from several instances.

        Parameters allow control of the set of instances used and how they
        are joined together, as well as post-processing of the result.

        Parameters
        ----------

        data_offset: duration, mandatory
            The duration added to the issue_date to find the start of the data
            fragment.  Format is an ISO-8601 duration string up to "days".

        data_max_length: duration, optional
            The longest duration selected from a single instance, mostly used
            to detect missing instances.  ISO-8601 duration string up to "days".

        issue_date_from: time-stamp, optional
            Limits the timerange used to select instances.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps used to select instances.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        issue_weekdays: list of strings, optional
            Limits the instances to those matching the given weekdays.

        issue_days: list of integers, optional
            Limits the instances to those matching the given days of month.

        issue_months: list of strings, optional
            Limits the instances to those matching the given months.

        issue_times: list of strings, optional
            Limits the instances to those matching the given times of day.
            Format is 'HH', 'HH:mm' or 'HH:mm:ss'.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be determined by the first
            selected instance and the data_offset parameter. If only the date
            (without time) is given, the time is assumed to be 00:00. The
            timestamp can be provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available in the last instance selected,
            optionally limited by the data_max_length parameter.

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
        args = [util.make_arg('data_offset', '{}'.format(data_offset))]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        self._add_from_to(args, data_from, data_to, prefix='data_')
        self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if data_max_length is not None:
            args.append(util.make_arg('data_max_length', data_max_length))
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
        astr = '&'.join(args)
        url = '/api/instances/{}/relative?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.INSTANCES)

    def get_absolute(self, data_date, issue_frequency=None, issue_date_from=None, issue_date_to=None):
        """ Get an absolute forecast from the INSTANCE curve

        An absolute forecast is a time series created by selecting a single
        data date from a range of instances, using the issue_date as
        data date in the result.

        Parameters
        ----------

        data_date: time-stamp, mandatory
            The data date of the absolute forecast.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_frequency: str, optional
            The frequency of the returned time series.  Mandatory if the
            issue frequency of the curve is 'ANY'.  Data will only be
            returned for those instances whose issue_date is compatible
            with issue_frequency.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        issue_date_from: time-stamp, optional
            The start of the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "data_date".

        issue_date_to: time-stamp, optional
            The end of the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "data_date".

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args = [util.make_arg('data_date', data_date)]
        if issue_frequency is not None:
            args.append(util.make_arg('issue_frequency', issue_frequency))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        astr = '&'.join(args)
        url = '/api/instances/{}/absolute?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
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
                         output_time_zone=None, only_accessible=None, modified_since=None):
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
            Format is 'HH', 'HH:mm' or 'HH:mm:ss'.

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

        modified_since: datestring, pandas.Timestamp or datetime.datetime
            only return instances that where modified after given datetime.

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower())]
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
                     output_time_zone=None, only_accessible=None):
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
            Time-stamp representing the issue date to get data for.
            The timestamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        tag: str or list, optional
            tag or tags to get the data for. If omitted, the default
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

        Returns
        -------
        :class:`wapi.util.TS` object
        """

        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower()),
              util.make_arg('issue_date', issue_date)]
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
                   function=None, frequency=None, output_time_zone=None, only_accessible=None):
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

        Returns
        -------
        :class:`wapi.util.TS` object
        """

        if only_accessible is not None:
            warnings.warn("only_accessible parameter will be removed soon.", FutureWarning, stacklevel=2)
        args=[util.make_arg('with_data', '{}'.format(with_data).lower())]
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


    def get_relative(self, data_offset, data_max_length=None, tag=None, issue_date_from=None, issue_date_to=None,
                     issue_dates=None, issue_weekdays=None, issue_days=None, issue_months=None, issue_times=None,
                     data_from=None, data_to=None, time_zone=None, filter=None, function=None,
                     frequency=None, output_time_zone=None):
        """ Get a relative forecast from the TAGGED INSTANCE curve

        A relative forecast is a time series created by joining multiple
        instances so that the data date is issue_date + data_offset.
        If the data frequency is higher than the frequency of the selected
        instances, a range of data values from each instance will be used.
        Similarly if the issue frequency is higher than the data frequency,
        the same data date will be used from several instances.

        Parameters allow control of the set of instances used and how they
        are joined together, as well as post-processing of the result.

        Parameters
        ----------

        data_offset: duration, mandatory
            The duration added to the issue_date to find the start of the data
            fragment.  Format is an ISO-8601 duration string up to "days".

        data_max_length: duration, optional
            The longest duration selected from a single instance, mostly used
            to detect missing instances.  ISO-8601 duration string up to "days".

        tag: str, optional
            tag to get the data for. If omitted, the default tag is used.

        issue_date_from: time-stamp, optional
            Limits the timerange used to select instances.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_date_to: time-stamp, optional
            Limits the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "issue_date_from".

        issue_dates: list of time-stamps, optional
            List of timestamps used to select instances.
            The time-stamps can be provided in the same types as
            "issue_date_from".

        issue_weekdays: list of strings, optional
            Limits the instances to those matching the given weekdays.

        issue_days: list of integers, optional
            Limits the instances to those matching the given days of month.

        issue_months: list of strings, optional
            Limits the instances to those matching the given months.

        issue_times: list of strings, optional
            Limits the instances to those matching the given times of day.
            Format is 'HH', 'HH:mm' or 'HH:mm:ss'.

        data_from: time-stamp, optional
            start date (and time) of data to be fetched. If not given, the start
            date of the returned timeseries will be determined by the first
            selected instance and the data_offset parameter. If only the date
            (without time) is given, the time is assumed to be 00:00. The
            timestamp can be provided in the same types as "issue_date_from".

        data_to: time-stamp, optional
            end date (and time) of data to be fetched. The time-stamp can be
            provided in the same types as "issue_date_from".
            End dates are always excluded in the result!
            If not given, the end date of the returned timeseries will be
            the last date with data available in the last instance selected,
            optionally limited by the data_max_length parameter.

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
        args = [util.make_arg('data_offset', '{}'.format(data_offset))]
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        self._add_from_to(args, data_from, data_to, prefix='data_')
        self._add_functions(args, time_zone, filter, function, frequency, output_time_zone)
        if data_max_length is not None:
            args.append(util.make_arg('data_max_length', data_max_length))
        if tag is not None:
            args.append(util.make_arg('tag', tag))
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
        astr = '&'.join(args)
        url = '/api/instances/tagged/{}/relative?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.TAGGED_INSTANCES)

    def get_absolute(self, data_date, issue_frequency=None, tag=None, issue_date_from=None, issue_date_to=None):
        """ Get an absolute forecast from the INSTANCE curve

        An absolute forecast is a time series created by selecting a single
        data date from a range of instances, using the issue_date as
        data date in the result.

        Parameters
        ----------

        data_date: time-stamp, mandatory
            The data date of the absolute forecast.
            The time-stamp can be provided in any of the following types :

            * datestring in format '%Y-%M-%DT%h:%m:%sZ',
              eg '2017-01-01' or '2018-12-16T13:45:00Z'
            * pandas.Timestamp object
            * datetime.datetime object

        issue_frequency: str, optional
            The frequency of the returned time series.  Mandatory if the
            issue frequency of the curve is 'ANY'.  Data will only be
            returned for those instances whose issue_date is compatible
            with issue_frequency.
            You can find valid values for this by calling
            :meth:`wapi.session.Session.get_frequencies`.

        tag: str, optional
            tag to get the data for. If omitted, the default tag is used.

        issue_date_from: time-stamp, optional
            The start of the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "data_date".

        issue_date_to: time-stamp, optional
            The end of the timerange used to select instances.
            The time-stamp can be provided in the same types as
            "data_date".

        Returns
        -------
        :class:`wapi.util.TS` object
        """
        args = [util.make_arg('data_date', data_date)]
        if issue_frequency is not None:
            args.append(util.make_arg('issue_frequency', issue_frequency))
        if tag is not None:
            args.append(util.make_arg('tag', tag))
        self._add_from_to(args, issue_date_from, issue_date_to, prefix='issue_date_')
        astr = '&'.join(args)
        url = '/api/instances/tagged/{}/absolute?{}'.format(self.id, astr)
        result = self._load_data(url, 'Failed to find instances')
        if result is None:
            return result
        return util.TS(input_dict=result, curve_type=util.TAGGED_INSTANCES)
