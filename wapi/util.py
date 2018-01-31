#
# Various utility and conversion functions to make it easier to work with
# the data from the backend
#

import datetime
import dateutil.parser
import pytz
import pandas as pd
from builtins import str


def parsetime(datestr, tz=None):
    '''Parse the input date and optionally convert to correct time zone'''
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
    '''
    Parse a range object (a pair of date strings, which may each be None)
    '''
    try:
        begin, end = rangeobj
        if begin is not None:
            begin = parsetime(begin)
        if end is not None:
            end = parsetime(end)
        return (begin, end)
    except:
        raise ValueError('Malformed range: {}'.format(rangeobj))


class TS(object):
    '''A class to hold a basic time series.'''
    def __init__(self, input, tag=None):
        # input is the json dict from the data API
        if 'id' in input:
            self.id = input['id']
        if 'name' in input:
            self.name = input['name']
        self.frequency = input['frequency']
        if tag is not None:
            self.tag = tag
        try:
            self.tz = pytz.timezone(input['time_zone'])
        except:
            self.tz = pytz.utc
        self.index = []
        self.values = []
        for row in input['points']:
            if len(row) != 2:
                raise ValueError('Points have unexpected contents')
            self.index.append(datetime.datetime.fromtimestamp(row[0]/1000.0, self.tz))
            self.values.append(row[1])

    def to_pandas(self, name=None):
        if name is None and hasattr(self, 'tag'):
            name = self.tag
        if name is None:
            namestr = ''
        else:
            namestr = name + "-"
        res = pd.Series(name=name, index=self.index, data=self.values)
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


class Instance(TS):
    '''A class to hold an instance, which is a superset of a time series'''
    def __init__(self, input):
        super(Instance, self).__init__(input)
        if 'tag' in input:
            self.tag = input['tag']
        self.issue_date = parsetime(input['issue_date'], self.tz)

    def to_pandas(self):
        return TS.to_pandas(self, self.name)


def instance_DF(instance_list):
    '''Given a list of instances, create a DataFrame with the tag of each instance as column name'''
    return pd.DataFrame({i.tag: i.to_pandas() for i in instance_list})
