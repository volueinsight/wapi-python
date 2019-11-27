.. _examples:

Examples
========


TIME_SERIES curve examples
---------------------------

* Simple example how to read a TIME_SERIES curve
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_simple_read.py>`_ ,
  :download:`[download] <../examples/Timeseries_curve_examples/ts_simple_read.py>`)
* Aggregation example
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_aggregation.py>`_ ,
  :download:`[download] <../examples/Timeseries_curve_examples/ts_aggregation.py>`)
* Aggregation example - changing timezones
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_aggregation_timezone.py>`_ ,
  :download:`[download] <../examples/Timeseries_curve_examples/ts_aggregation_timezone.py>`)
* Filter example
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_filter.py>`_ ,
  :download:`[download] <../examples/Timeseries_curve_examples/ts_filter.py>`)
* Read multiple curves and save them as csv
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_get_multiple_curves.py>`_ ,
  :download:`[download] <../examples/Timeseries_curve_examples/ts_get_multiple_curves.py>`)


TAGGED curve examples
----------------------

* No example yet


INSTANCE curve examples
-------------------------

* Simple example how to read an INSTANCE curve
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Instance_curve_examples/ins_simple_read.py>`_ ,
  :download:`[download] <../examples/Instance_curve_examples/ins_simple_read.py>`)
* Get multiple instances
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Instance_curve_examples/ins_multiple_instances.py>`_ ,
  :download:`[download] <../examples/Instance_curve_examples/ins_multiple_instances.py>`)
* Get latest instance
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Instance_curve_examples/ins_latest_instance.py>`_ ,
  :download:`[download] <../examples/Instance_curve_examples/ins_latest_instance.py>`)
* Get multiple instance curves and save them as csv
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Instance_curve_examples/ins_get_multiple_curves.py>`_ ,
  :download:`[download] <../examples/Instance_curve_examples/ins_get_multiple_curves.py>`)



TAGGED_INSTANCE curve examples
--------------------------------

* Simple example how to read a TAGGED_INSTANCE curve and get available tags
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Tagged-Instance_curve_examples/tagins_simple_read.py>`_ ,
  :download:`[download] <../examples/Tagged-Instance_curve_examples/tagins_simple_read.py>`)
* Read data for multiple tags
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Tagged-Instance_curve_examples/tagins_multiple_tags.py>`_ ,
  :download:`[download] <../examples/Tagged-Instance_curve_examples/tagins_multiple_tags.py>`)
* Get multiple instances
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Tagged-Instance_curve_examples/tagins_multiple_instances.py>`_ ,
  :download:`[download] <../examples/Tagged-Instance_curve_examples/tagins_multiple_instances.py>`)
* Get latest instance
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Tagged-Instance_curve_examples/tagins_latest_instance.py>`_ ,
  :download:`[download] <../examples/Tagged-Instance_curve_examples/tagins_latest_instance.py>`)


Listening for changes example
-----------------------------

* Listening for changes for several Solar and Wind curves and append new data to
  a csv file for each new event
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/Listening_for_changes/renewables_database.py>`_ ,
  :download:`[download] <../examples/Listening_for_changes/renewables_database.py>`)

General examples
-----------------

* Comparing PV forecast and actuals
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/general_examples/gen_pv_actuals_vs_forecast.py>`_ ,
  :download:`[download] <../examples/general_examples/gen_pv_actuals_vs_forecast.py>`)
* Combining Series to DataFrame in pandas
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/general_examples/gen_series_to_frame.py>`_ ,
  :download:`[download] <../examples/general_examples/gen_series_to_frame.py>`)
* Saving pandas Series and DataFrames to csv and xlsx
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/general_examples/gen_save_pandas.py>`_ ,
  :download:`[download] <../examples/general_examples/gen_save_pandas.py>`)
* Aggregation examples using pandas
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/general_examples/gen_aggregation_pandas.py>`_ ,
  :download:`[download] <../examples/general_examples/gen_aggregation_pandas.py>`)

Intraday price forecast examples
--------------------------------

* Simple example on how to get the intraday price forecast and on how th get the latest intraday price forecast.
(`[view on github] <https://github.com/wattsight/wapi-python/blob/development/examples/intraday_examples/intraday_price_forecast.py>`_ ,
:download:`[download] <../examples/intraday_examples/intraday_price_forecast.py>`)
* Example on how to get the absolute forecast for the intraday price. The absolute forecast shows the price development over time for a 
specific contract.
(`[view on github] <https://github.com/wattsight/wapi-python/blob/development/examples/intraday_examples/absolute_intraday_price_forecast.py>`_ ,
:download:`[download] <../examples/intraday_examples/absolute_intraday_price_forecast.py>`) 

Reproduce figures from wattsight.com
-------------------------------------

* Reproduce one of the 4 following Fundamental figures for any region
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/reproduce_wattsight_plots/ws_fundamentals_hourly.py>`_ ,
  :download:`[download] <../examples/reproduce_wattsight_plots/ws_fundamentals_hourly.py>`)


  .. figure:: img/con_de.png
     :width: 40%
     :align: center

     Consumption https://app.wattsight.com/#tab/power/115/2


  .. figure:: img/pro_de_spv.png
     :width: 40%
     :align: center

     Photovoltaic https://app.wattsight.com/#tab/power/135/2


  .. figure:: img/pro_de_wnd.png
     :width: 40%
     :align: center

     Wind https://app.wattsight.com/#tab/power/126/2


  .. figure:: img/rdl_de.png
     :width: 40%
     :align: center

     Residual Load https://app.wattsight.com/#tab/power/109/2

* Reproduce temperature figures for any region
  (`[view on github] <https://github.com/wattsight/wapi-python/blob/master/examples/reproduce_wattsight_plots/ws_temperature_hourly.py>`_ ,
  :download:`[download] <../examples/reproduce_wattsight_plots/ws_temperature_hourly.py>`)

    .. figure:: img/temp_de.png
     :width: 40%
     :align: center

     Temperature https://app.wattsight.com/#tab/power/245/2
