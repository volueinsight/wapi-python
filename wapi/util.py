#
# Various utility and conversion functions to make it easier to work with
# the data from the backend
#

import datetime
import dateutil.parser
import pytz
import pandas as pd
from builtins import str


# Curve types
TIME_SERIES = 'TIME_SERIES'
TAGGED = 'TAGGED'
INSTANCES = 'INSTANCES'
TAGGED_INSTANCES = 'TAGGED_INSTANCES'


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
        if input_dict is not None:
            for attr in ('id', 'name', 'frequency', 'time_zone', 'tag', 'issue_date', 'curve_type', 'points'):
                if attr in input_dict:
                    setattr(self, attr, input_dict[attr])
        #
        try:
            self.tz = pytz.timezone(input['time_zone'])
        except:
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

        attrs.extend([self.data_type, str(self.tz), self.frequency])

        if self.tag:
            attrs.append(self.tag)
        if self.issue_date:
            attrs.append(self.issue_date.strftime('%Y-%m-%d'))
        if self.points:
            attrs.append('size: {}'.format(len(self.points)))

        return ' '.join(attrs)

    def to_pandas(self, name=None):
        if name is None:
            name = self.name or self.id
        if self.points is None:
            return pd.Series(name=name)
        #
        index = []
        values = []
        for row in self.points:
            if len(row) != 2:
                raise ValueError('Points have unexpected contents')
            index.append(datetime.datetime.fromtimestamp(row[0]/1000.0, self.tz))
            values.append(row[1])
        res = pd.Series(name=name, index=index, data=values)
        return res.asfreq(self._map_freq(self.frequency))

    @staticmethod
    def _map_freq(frequency):
        freqTable = {
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

        if frequency.upper() in freqTable:
            frequency = freqTable[frequency.upper()]
        return frequency


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
        # Convert timestamp to given tz
        if isinstance(tz, str):
            tz = pytz.timezone(tz)
        try:
            d = d.astimezone(tz)
        except ValueError:
            # This means that d does not already have zone info,
            # assume the supplied tz is the right one
            d = d.replace(tzinfo=tz)
    else:
        # If datestr does not have tzinfo and no tz given, assume CET
        if d.tzinfo is None:
            d = d.replace(tzinfo=pytz.timezone('CET'))
    return d


def parserange(rangeobj, tz=None):
    """
    Parse a range object (a pair of date strings, which may each be None)
    """
    try:
        begin, end = rangeobj
        if begin is not None:
            begin = parsetime(begin)
        if end is not None:
            end = parsetime(end)
        return (begin, end)
    except:
        raise ValueError('Malformed range: {}'.format(rangeobj))


def parse_tz(time_zone):
    try:
        # TODO: Add more fancy implementation of the gas time zones?
        if time_zone == 'CEGT':
            time_zone = 'CET'
        if time_zone == 'WEGT':
            time_zone = 'WET'
        return pytz.timezone(time_zone)
    except:
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
