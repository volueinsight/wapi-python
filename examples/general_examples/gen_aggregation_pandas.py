"""
This simple example reads data from an TIME_SERIES curve and aggregates it
using pandas. 
This example shows the same results as the TIME_SERIES aggregation
example, where the data is aggregated in the backend:
https://github.com/wattsight/wapi-python/blob/master/examples/Timeseries_curve_examples/ts_aggregation.py
Have a look at the pandas documentation for further information:
https://wattsight-wapi-python.readthedocs-hosted.com/en/latest/index.html
"""
import wapi
import pandas as pd
import matplotlib.pyplot as plt

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################


# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# Define start and end time
# start_date
start_date = pd.Timestamp('2018-6-1 00:00')
# end_date
end_date =  pd.Timestamp('2018-6-8 00:00')
  
# define curve name to read, in this case temperature for Germany
curve_name = 'tt de con °c cet min15 s'
# get the curve
curve = session.get_curve(name=curve_name)

## No aggregation
# read curve data from start_date to end_date to ts object
ts15min = curve.get_data(data_from=start_date, data_to=end_date)
# convert to pandas.Series object
s15min = ts15min.to_pandas()

## Hourly average aggregation
# aggregate Series to hourly average data
s1h = s15min.groupby(pd.Grouper(freq='H')).mean()

## 6 Hourly average aggregation
# aggregate Series to 6-hourly average data
s6h = s15min.groupby(pd.Grouper(freq='6H')).mean()

## Daily average aggregation
# aggregate Series to daily average data
s1d = s15min.groupby(pd.Grouper(freq='D')).mean()

## Daily max aggregation
# aggregate Series to daily max data
s1dmax = s15min.groupby(pd.Grouper(freq='D')).max()

## Daily min aggregation
# aggregate Series to daily min data
s1dmin = s15min.groupby(pd.Grouper(freq='D')).min()

# plot curves using matplotlib
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(s15min, label='15 minutes')
ax.step(s1h.index, s1h.values, label='1 hour', where='post', linestyle=':')
ax.step(s6h.index, s6h.values, label='6 hours', where='post')
ax.step(s1d.index, s1d.values, label='1 day average', where='post')
ax.step(s1dmax.index, s1dmax.values, label='1 day max', where='post')
ax.step(s1dmin.index, s1dmin.values, label='1 day min', where='post')
ax.legend()

# show the figure
plt.show()
