"""
This simple example reads aggregated data from an TIME_SERIES curve
Have a look at the documentation for further information:
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
# read curve data from start_date to end_date to ts object and
# aggregate to hourly frequency
ts1h = curve.get_data(data_from=start_date, data_to=end_date, function='AVERAGE',
                    frequency='H')
# convert to pandas.Series object
s1h = ts1h.to_pandas()

## 6 Hourly average aggregation
# read curve data from start_date to end_date to ts object and
# aggregate to 6 hourly frequency
ts6h = curve.get_data(data_from=start_date, data_to=end_date, function='AVERAGE',
                    frequency='H6')
# convert to pandas.Series object
s6h = ts6h.to_pandas()

## Daily average aggregation
# read curve data from start_date to end_date to ts object and
# aggregate to daily average
ts1d = curve.get_data(data_from=start_date, data_to=end_date, function='AVERAGE',
                    frequency='D')
# convert to pandas.Series object
s1d = ts1d.to_pandas()

## Daily max aggregation
# read curve data from start_date to end_date to ts object and
# aggregate to daily max
ts1dmax = curve.get_data(data_from=start_date, data_to=end_date, function='MAX',
                    frequency='D')
# convert to pandas.Series object
s1dmax = ts1dmax.to_pandas()

## Daily min aggregation
# read curve data from start_date to end_date to ts object and
# aggregate to daily min
ts1dmin = curve.get_data(data_from=start_date, data_to=end_date, function='MIN',
                    frequency='D')
# convert to pandas.Series object
s1dmin = ts1dmin.to_pandas()

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
