#
# Various utility and conversion functions to make it easier to work with
# the data from the backend
#

import calendar
import datetime
import dateutil.parser
import pytz
import pandas as pd

# Curve types
TIME_SERIES = 'TIME_SERIES'
TAGGED = 'TAGGED'
INSTANCES = 'INSTANCES'
TAGGED_INSTANCES = 'TAGGED_INSTANCES'


# Frequency mapping from TS to Pandas
_TS_FREQ_TABLE = {
    'Y': 'AS',
    'S': '2QS',
    'Q': 'QS',
    'M': 'MS',
    'W': 'W-MON',
    'H12': '12H',
    'H6': '6H',
    'H3': '3H',
    'MIN30': '30T',
    'MIN15': '15T',
    'MIN5': '5T',
}
# Mapping from Pandas to TS is built from map above
_PANDAS_FREQ_TABLE = {}
for k, v in _TS_FREQ_TABLE.items():
    _PANDAS_FREQ_TABLE[v] = k


class CurveException(Exception):
    pass


class TS(object):
    """
    A class to hold a basic time series.
    """
    def __init__(self, id=None, name=None, frequency=None, time_zone=None, tag=None, issue_date=None,
                 curve_type=None, points=None, input_dict=None):
        self.id = id
        self.name = name
        self.frequency = frequency
        self.time_zone = time_zone
        self.tag = tag
        self.issue_date = issue_date
        self.data_type = curve_type
        self.points = points
        #
        # input_dict is the json dict from WAPI
        attributes = ('id', 'name', 'frequency', 'time_zone',
                      'tag', 'issue_date', 'curve_type', 'points')
        if input_dict is not None:
            for attr in attributes:
                if attr in input_dict:
                    setattr(self, attr, input_dict[attr])

        if self.time_zone is not None:
            self.tz = parse_tz(self.time_zone)
        else:
            self.tz = pytz.timezone('CET')

        if self.data_type is None:
            self.data_type = detect_data_type(issue_date, tag)
        # Validation
        if self.id is None and self.name is None:
            raise CurveException('TS must have id or name')
        if self.frequency is None:
            raise CurveException('TS must have frequency')

    def __str__(self):
        attrs = ['TS:']
        if self.id:
            attrs.append(str(self.id))
        if self.name:
            attrs.append(self.name)

        attrs.extend([self.data_type, self.tz.zone, self.frequency])

        if self.tag:
            attrs.append(self.tag)
        if self.issue_date:
            attrs.append(self.issue_date.strftime('%Y-%m-%d'))
        if self.points:
            attrs.append('size: {}'.format(len(self.points)))

        return ' '.join(attrs)

    def to_pandas(self, name=None):
        """ Converting :class:`wapi.util.TS` object to a pandas.Series object
                
        Parameters
        ----------      
        name: str, optional
            Name of the returned pandas.Series object. If not given the name 
            of the curve will be used.
        Returns
        -------
        pandas.Series   
        """
        if name is None:
            name = self.name or self.id
        if self.points is None:
            return pd.Series(name=name)

        index = []
        values = []
        for row in self.points:
            if len(row) != 2:
                raise ValueError('Points have unexpected contents')
            dt = datetime.datetime.fromtimestamp(row[0] / 1000.0, self.tz)
            index.append(dt)
            values.append(row[1])
        res = pd.Series(name=name, index=index, data=values)
        return res.asfreq(self._map_freq(self.frequency))

    @staticmethod
    def from_pandas(pd_series):
        name = pd_series.name
        frequency = TS._rev_map_freq(pd_series.index.freqstr)

        points = []
        for i in pd_series.index:
            t = i.astimezone(pytz.utc)
            timestamp = int(calendar.timegm(t.timetuple()) * 1000)
            points.append([timestamp, pd_series[i]])

        if is_integer(name):
            return TS(id=int(name), frequency=frequency, points=points)
        else:
            return TS(name=name, frequency=frequency, points=points)

    @staticmethod
    def _map_freq(frequency):
        if frequency.upper() in _TS_FREQ_TABLE:
            frequency = _TS_FREQ_TABLE[frequency.upper()]
        return frequency

    @staticmethod
    def _rev_map_freq(frequency):
        if frequency.upper() in _PANDAS_FREQ_TABLE:
            frequency = _PANDAS_FREQ_TABLE[frequency.upper()]
        return frequency

    @staticmethod
    def sum(ts_list, name):
        """ calculate the sum of a given list of :class:`wapi.util.TS` objects

        Returns a :class:`~wapi.util.TS` (:class:`wapi.util.TS`) object that is 
        the sum of a list of
        TS objects with the given name.
         
        Parameters
        ----------      
        ts_list: list
            list of TS objects
        name: str
            Name of the returned TS object.
        Returns
        -------
        :class:`wapi.util.TS` object
        """
        df = _ts_list_to_dataframe(ts_list)
        return _generated_series_to_TS(df.sum(axis=1), name)

    @staticmethod
    def mean(ts_list, name):
        """ calculate the mean of a given list of TS objects

        Returns a TS (:class:`wapi.util.TS`) object that is 
        the mean of a list of
        TS objects with the given name.
         
        Parameters
        ----------
        ts_list: list
            list of TS objects
        name: str
            Name of the returned TS object.
        Returns
        -------
        :class:`wapi.util.TS` object
        """
        df = _ts_list_to_dataframe(ts_list)
        return _generated_series_to_TS(df.mean(axis=1), name)

    @staticmethod
    def median(ts_list, name):
        """ calculate the median of a given list of TS objects

        Returns a TS (:class:`wapi.util.TS`) object that is 
        the median of a list of
        TS objects with the given name.
         
        Parameters
        ----------
        ts_list: list
            list of TS objects
        name: str
            Name of the returned TS object.
        Returns
        -------
        :class:`wapi.util.TS` object
        """
        df = _ts_list_to_dataframe(ts_list)
        return _generated_series_to_TS(df.median(axis=1), name)


def _generated_series_to_TS(series, name):
    series.name = name
    return TS.from_pandas(series)


def _ts_list_to_dataframe(ts_list):
    pd_list = []
    for ts in ts_list:
        pd_list.append(ts.to_pandas())

    return pd.concat(pd_list, axis=1)


def tags_to_DF(tagged_list):
    """
    Given a list of tagged series/instances, create a DataFrame with the tag of each as column name
    """
    return pd.DataFrame({s.tag: s.to_pandas() for s in tagged_list})


#
# Some parsing helpers
#


def parsetime(datestr, tz=None):
    """
    Parse the input date and optionally convert to correct time zone
    """

    d = dateutil.parser.parse(datestr)

    if tz is not None:
        if not isinstance(tz, datetime.tzinfo):
            tz = parse_tz(tz)

        if d.tzinfo is not None:
            d = d.astimezone(tz)
        else:
            d = tz.localize(d)

    else:
        # If datestr does not have tzinfo and no tz given, assume CET
        if d.tzinfo is None:
            d = pytz.timezone('CET').localize(d)
    return d


def parserange(rangeobj, tz=None):
    """
    Parse a range object (a pair of date strings, which may each be None)
    """
    begin, end = rangeobj
    if begin is not None:
        begin = parsetime(begin, tz=tz)
    if end is not None:
        end = parsetime(end, tz=tz)
    return (begin, end)


def parse_tz(time_zone):
    try:
        # TODO: Add more fancy implementation of the gas time zones?
        if time_zone == 'CEGT':
            time_zone = 'CET'
        if time_zone == 'WEGT':
            time_zone = 'WET'
        return pytz.timezone(time_zone)
    except pytz.exceptions.UnknownTimeZoneError:
        return pytz.timezone('CET')


def detect_data_type(issue_date, tag):
    if issue_date is None and tag is None:
        return TIME_SERIES
    elif issue_date is None:
        return TAGGED
    elif tag is None:
        return INSTANCES
    else:
        return TAGGED_INSTANCES


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
