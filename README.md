# wapi-python
Wattsight API python library

This library is meant as a simple toolkit for working with data from
https://api.wattsight.com/ (or equivalent services).  Note that access
is based on some sort of login credentials, this library is not all
that useful unless you have a valid Wattsight account.

The library is tested against both Python 2.7 and Python 3.6,
we recommend using Python 3.

A [Jupyter Notebook example](example/README.md) of using the library is available in the example folder.


## Session

In order to work with WAPI, first create a session.  A session can be configured
using a config file, or through calls:

```commandline
>>> import wapi
>>> session = wapi.Session(config_file='myconfig.ini')
```

or

```commandline
>>> import wapi
>>> session = wapi.Session(client_id='client id', client_secret='client secret')
```

For both methods, it is possible to override the base url for the API using the `urlbase`
parameter.  When specifying the `client_id`/`client_secret` it is also possible to
override the authentication server url using the `auth_urlbase` parameter.
(Both can also be specified in the configuration file, see `sampleconfig.ini` for details.)

## Curves

Key in our API is the notion of curves.  A curve is a collection of metadata, describing
one or more time series.  There are 4 types of curves: TIME_SERIES, TAGGED, INSTANCES
and TAGGED_INSTANCES.

The metadata attributes that a curve can have are: `commodity`, `categories`, `area`,
`border_source`, `station`, `sources`, `scenarios`, `unit`, `time_zone`, `version`,
`frequency` and `data_type`.  In addition it will have `id`, `name`, `curve_state`
and `curve_type`.

The standard way of finding curves, is by searching using a combination of these metadata
attributes.  It is also possible to search using a free-text query, by ids and by names.
A search call will return a list of 0 or more curve objects:

```commandline
>>> curves = session.search(category='WND', area=['EE', 'LT'], frequency='H')
>>> [c.name for c in curves]
['pro ee wnd intraday ec00da mwh/h cet h f',
 'pro ee wnd intraday lastec mwh/h cet h f',
 'pro ee wnd intraday tso mwh/h cet h f',
 'pro lt wnd intraday ec00da mwh/h cet h f',
 'pro lt wnd intraday lastec mwh/h cet h f',
 'pro lt wnd intraday tso mwh/h cet h f',
 'pro ee wnd intraday mwh/h cet h a',
 'pro lt wnd intraday mwh/h cet h a']
```

When supplying a list of alternatives the search is for "any of" the values,
while the search is for the combination of attributes requested ("and").

It is also possible to fetch a single curve by id or name using:

```commandline
>>> curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
>>> curve.id
2206
```

Please note that we may occasionally have to change the IDs of curves, so please treat
these IDs as ephemeral values.  In order to fetch a particular curve, use the name.

### Valid attribute values

The set of valid values for the various metadata attributes can be retrieved:

```commandline
>>> units = session.get_attribute('units')
>>> print(units)
[{'key': 'MW', 'name': 'MW', 'description': ''}, {'key': '€/MWh', 'name': 'Euro per MWh', 'description': ''}]
```


## Getting data from curves

Each curve type has a separate set of methods for getting the time series.

### Time Series curves

This is the simplest curve type, it holds a single time series.  This is used for
actual values, backcasts, normals, etc.  To fetch the data, use the `get_data` call:

```commandline
>>> curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
>>> ts = curve.get_data(data_from="2018-01-01", data_to="2018-01-05", frequency="D", function="SUM")
>>> ts.to_pandas()
2018-01-01 00:00:00+01:00    2169.0
2018-01-02 00:00:00+01:00    3948.0
2018-01-03 00:00:00+01:00    1489.0
2018-01-04 00:00:00+01:00    1860.0
Freq: D, Name: pro ee wnd intraday mwh/h cet h a, dtype: float64
```

Observe that it is possible to process the curve directly in the API, this can be used with
great effect to reduce the amount of data retrieved if the full set of details is not needed.
See the REST API documentation for details on what processing is available.

All time series are returned in a `TS` object (`wapi.util.TS`), which is a simple holding
class which will store associated data.  Its most useful function is the `to_pandas` function
demonstrated above, which will return a standard Pandas `Series` object.
The inverse method `TS.from_pandas(series)` will turn the Pandas `Series` object back into a `TS` object.

The `TS` class also contains some simple aggregation functions
* `TS.sum(ts_list, name)` returns a TS object that is the sum of a list of TS objects with the given name
* `TS.mean(ts_list, name)` returns a TS object that is the mean of a list of TS objects with the given name
* `TS.median(ts_list, name)` returns a TS object that is the median of a list of TS objects with the given name


### Tagged curves

A tagged curve holds a set of closely related time series, each identified by a tag.  The most
common use of tags is for ensemble weather data.  The existing set of tags can be found
with `get_tags`, while the `get_data` call can take a `tag` parameter:

```commandline
>>> tags = curve.get_tags()
>>> ts = curve.get_data(tag='Avg', ...)
```

Tag can be a single value or a list of values.  If omitted, it defaults to all available tags.
When a list of tags is requested, a list of time series is returned.


### Instance curves

A curve of instances is a bit more complex.  This is typically a forecast, and contains
a time series for each `issue_date` of the forecast.  It is possible to search for instances,
fetch a single instance (identified by issue_date), or to fetch the latest instance in a range:

```commandline
>>> lst = curve.search_instances(issue_date_from='2018-01-01T13:00', issue_date_to='2018-01-01T15:00')
>>> [i.issue_date for i in lst]
['2018-01-01T13:45:00Z',
 '2018-01-01T13:30:00Z',
 '2018-01-01T13:15:00Z',
 '2018-01-01T13:00:00Z',
 '2018-01-01T12:45:00Z',
 '2018-01-01T12:30:00Z',
 '2018-01-01T12:15:00Z',
 '2018-01-01T12:00:00Z']

>>> i = curve.get_instance(issue_date='2018-01-01T13:15:00Z')
>>> i.to_pandas()
2018-01-01 15:00:00+01:00     65.310897
2018-01-01 16:00:00+01:00     67.510937
...
2018-01-02 22:00:00+01:00    167.469376
2018-01-02 23:00:00+01:00    161.208839
Freq: H, Name: pro ee wnd intraday ec00da mwh/h cet h f, dtype: float64
```

Remember that the end dates are always excluded in the result:

```commandline
>>> i = curve.get_latest(issue_date_to='2018-01-01T14:00Z')
>>> i.issue_date
'2018-01-01T13:45:00Z'

>>> i = curve.get_latest(issue_date_to='2018-01-01T14:00:01Z')
>>> i.issue_date
'2018-01-01T14:00:00Z'
```

Whenever returning a time series, all the processing arguments are available in order to
change the returned values as needed.


### Tagged instance curves

Tagged instances are exactly the same extension over instances as tagged curves are over
time series curves.  There is a `get_tags` call to find available tags, `get_instance`
must be given `issue_date` while `tag` works as for tagged curves, and the search/latest
functions can take a list of tags to limit the search to only those tags.


## Events

Instead of having to poll the API for updated values, there is an event API available:

```commandline
>>> curve = session.get_curve(name='pro ee wnd intraday ec00da mwh/h cet h f')
>>> event_listener = session.events(curve)
```

It is possible to listen on several curves in the same listener (within reason).
This event listener is an iterable object, so it can simply be used in a loop:

```commandline
>>> for event in event_listener:
>>>     ... process event ...
```

It is also possible to retrieve a single event using `get`:

```commandline
>>> event = event_listener.get()
>>> event.issue_date
datetime.datetime(2018, 1, 2, 22, 45, tzinfo=tzutc())
>>> event.curve.name
'pro ee wnd intraday ec00da mwh/h cet h f'
```
