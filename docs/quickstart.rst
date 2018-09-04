.. _quickstart:

Quickstart
===========

1. Install with::

    $ pip install -U wapi-python
    
2. Import wapi and create a :class:`~wapi.session.Session` to connect to the database using 
   your `authentication credentials`_ ::
  
        import wapi
        session = wapi.Session(client_id='client id', client_secret='client secret')
  
3. Get a curve object by its name and fetch data from the curve. There are
   4 different curve types: TIME_SERIES, TAGGED, INSTANCES and TAGGED_INSTANCES.
   Each curve type has a separate set of methods for getting the time series.
   Each method will return a :class:`~wapi.util.TS` object, 
   containing the data of the curve::
   
        ## TIME_SERIES curve
        curve = session.get_curve(name='tt de con °c cet min15 s')
        ts = curve.get_data(data_from="2018-06-01", data_to="2018-06-08")
        
        ## TAGGED curve
        curve = session.get_curve(name='name of tagged curve')
        # TAGGED curves contain a timeseries for each defined tag.
        # Get available tags with: tags = curve.get_tags()
        ts = curve.get_data(tag='Avg', data_from="2018-01-01", data_to="2018-01-05")       
        
        
        ## INSTANCES curve
        curve = session.get_curve(name='tt de con ec00 °c cet min15 f')
        # INSTANCES curves contain a timeseries for each defined issue dates
        # Get a list of available curves with issue dates within a timerange with: 
        # curve.search_instances(issue_date_from='2018-01-01', issue_date_to='2018-01-01')
        ts = curve.get_instance(issue_date='2018-01-01T00:00')
        
        ## TAGGED_INSTANCES curve
        curve = session.get_curve(name='tt de con ec00ens °c cet min15 f')
        # TAGGED_INSTANCES curves contain a timeseries for each combination of 
        # defined issue dates and tags.
        # A TAGGED_INSTANCES is a combination of a TAGGED curve and INSTANCES curve
        ts = curve.get_instance(issue_date='2018-01-01T00:00', tag='Avg')
        
        
4. Convert :class:`~wapi.util.TS` object to a `pandas.Series`_ or 
   `pandas.DataFrame`_ to work 
   with the data::
   
        pd_s = ts.to_pandas() # convert TS object to pandas.Series object
        pd_df = pd_s.to_frame() # convert pandas.Series to pandas.DataFrame
 
 
.. note::
    
    Each curve object has the attribute `curve.curve_type`, specifying the type
    of the given curve::

        >>> curve = session.get_curve(name='tt de con °c cet min15 s')
        >>> curve.curve_type # check the type of the given curve
        'TIME_SERIES'


.. _authentication credentials: https://auth.wattsight.com/account/oauth-clients
.. _pandas.Series: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html
.. _pandas.DataFrame: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html