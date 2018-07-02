.. _curves:

Access data from WAPI
=====================

The data in WAPI is stored in `curves` . A curve is a collection of metadata, 
describing one or more time series. 
There are 4 types of curves: 

* TIME_SERIES
* TAGGED
* INSTANCES
* TAGGED_INSTANCES

This chapter describes how to search for available curves in WAPI and
how to access the stored data, based on the given curve type.

.. _search-curves:
  
Searching for curves
--------------------

Each curve can have various of the following `metadata` attributes that 
describe the curve:
 
* commodity
* categories
* area
* border_source
* station
* sources 
* scenarios
* unit
* time_zone
* version
* frequency
* data_type 

The standard way of finding curves, is by searching using a combination of these 
metadata attributes. To search for curves, you can either
use the `api web interface`_ (see the `documentation`_ for more info) 
or search for curves within python.

To search for curves within python, use the :meth:`wapi.session.Session.search` 
function.
When supplying a list of alternatives the search is for "any of" the values, 
while the search is for the combination of attributes requested ("and").
A search call will return a list of 0 or more curve objects. You can 
get the name of the found curve(s) by accessing the `curve.name` attribute::

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
     
.. automethod:: wapi.session.Session.search
    :noindex:     


Getting a curve object
-----------------------

In order to fetch data from WAPI, you first have to fetch the curve you want
to read the data from. You can either do this by  
:ref:`searching for curves<search-curves>` ,
since this will already return a list of curve objects. Or you can get
a curve object by its name using the :meth:`wapi.session.Session.get_curve` 
method::

    curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
    
Each curve has all of the following `attributes` :

* id: id of the curve
* name: name of the curve
* curve_state: NOT SURE IF THAT SHOULD BE PUBLIC
* curve_type: one of the 4 defines types (TIME_SERIES, TAGGED, INSTANCES and 
  TAGGED_INSTANCES)    

The value of the attribute can be accessed with `curve.attribute_name`, eg ::

    >>> curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
    >>> curve.name
    pro ee wnd intraday mwh/h cet h a
    >>> curve.curve_type
    TIME_SERIES
    
.. automethod:: wapi.session.Session.get_curve
    :noindex:   

 
Getting data from a curve object
---------------------------------

There is a different method to get data for each of the 4 types of curves 
(TIME_SERIES, TAGGED, INSTANCES, TAGGED_INSTANCES)

To find out the type of a given curve, use the `curve.curve_type` attribute::

    >>> curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
    >>> curve.curve_type # check the type of the given curve
    'TIME_SERIES'


Getting data from a TIME_SERIES curve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A Time Series curves holds a single time series. 
This is used for actual values, backcasts, normals, etc. 
To get data from a Times Series curve, use the 
:meth:`~wapi.curves.TimeSeriesCurve.get_data` method
( :meth:`wapi.curves.TimeSeriesCurve.get_data` ). You can get the data as it
is stored in the curve, by defining a start date (`data_from`) and 
an end date (`data_to`) ::

    curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
    ts = curve.get_data(data_from='2018-01-01T14:00Z', data_to='2018-02-01T14:00Z')


.. note::
    End dates are always excluded in the result!
    
The :meth:`~wapi.curves.TimeSeriesCurve.get_data`  method returns 
a :class:`~wapi.util.TS` object (:class:`wapi.util.TS`). 
:ref:`Here you can see how to work with an TS object<use-TS>` .

It is possible to process curves directly in the API (eg aggregating to 
daily/weekly/monthly/yearly values) by using additional inputs to the
:meth:`~wapi.curves.TimeSeriesCurve.get_data`
method. This can be used with great effect to reduce the amount of 
data retrieved if the full set of details is not needed.
Have a look at the detailed method documentation below and at our
:ref:`examples<examples>` . 


.. automethod:: wapi.curves.TimeSeriesCurve.get_data
    :noindex: 

Getting data from a TAGGED curve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TBD


.. automethod:: wapi.curves.TaggedCurve.get_tags
    :noindex: 

.. automethod:: wapi.curves.TaggedCurve.get_data
    :noindex: 



Getting data from a INSTANCES curve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TBD


.. automethod:: wapi.curves.InstanceCurve.search_instances
    :noindex: 


.. automethod:: wapi.curves.InstanceCurve.get_instance
    :noindex:     
    
.. automethod:: wapi.curves.InstanceCurve.get_latest
    :noindex: 
    

Getting data from a TAGGED_INSTANCES curve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TBD

.. automethod:: wapi.curves.TaggedInstanceCurve.get_tags
    :noindex: 

.. automethod:: wapi.curves.TaggedInstanceCurve.search_instances
    :noindex: 


.. automethod:: wapi.curves.TaggedInstanceCurve.get_instance
    :noindex:     
    
.. automethod:: wapi.curves.TaggedInstanceCurve.get_latest
    :noindex:    

.. _use-TS:
    
Working with data from a curve object
--------------------------------------

Independent from the curve type and the respective method to get the data,
all these methods return a :class:`~wapi.util.TS` object 
(:class:`wapi.util.TS`).

The most important function of the :class:`~wapi.util.TS` class, is the 
:meth:`~wapi.util.TS.to_pandas` function, 
which will return a `pandas.Series`_ object with a date index, containing the
data of the curve::

    >>> curve = session.get_curve(name='pro ee wnd intraday mwh/h cet h a')
    >>> ts = curve.get_data(data_from="2018-01-01", data_to="2018-01-05",
    >>>                     frequency="D", function="SUM")
    >>> ts.to_pandas()
    2018-01-01 00:00:00+01:00    2169.0
    2018-01-02 00:00:00+01:00    3948.0
    2018-01-03 00:00:00+01:00    1489.0
    2018-01-04 00:00:00+01:00    1860.0
    Freq: D, Name: pro ee wnd intraday mwh/h cet h a, dtype: float64

Have a look at our :ref:`examples<examples>` or at 
the `pandas documentation`_ , to see how to work
with `pandas.Series`_ or `pandas.DataFrame`_ objects.

.. automethod:: wapi.util.TS.to_pandas
    :noindex: 


The :class:`~wapi.util.TS` class contains some simple aggregation functions, which can be 
used directly on a :class:`~wapi.util.TS` object:  
:meth:`~wapi.util.TS.sum` , :meth:`~wapi.util.TS.mean`
and :meth:`~wapi.util.TS.median` .

.. automethod:: wapi.util.TS.sum
    :noindex: 

.. automethod:: wapi.util.TS.mean
    :noindex: 
  
.. automethod:: wapi.util.TS.median
    :noindex: 



`pandas documentation`_
`pandas.Series`_
`pandas.DataFrame`_


    
 
.. _api web interface: https://api.wattsight.com/
.. _documentation: https://api.wattsight.com/#documentation
.. _pandas.Series: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html
.. _pandas.DataFrame: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
.. _pandas documentation: https://pandas.pydata.org/pandas-docs/stable/index.html

