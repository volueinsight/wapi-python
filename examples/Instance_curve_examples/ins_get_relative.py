"""
This example fetches a relative forecast from an INSTANCE curve that contains our forecast for wind
production based on the ec00 weather forecast. A relative forecast is a conjunction of fragments of 
selected instances. Have a look at the documentation for further information:
https://volueinsight.com/docs/api/api-absolute-relative-forecast.html?highlight=relative
"""

import wapi
import pandas as pd
import matplotlib.pyplot as plt

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
# Create a session to connect to Wattsight Database.
session = wapi.Session(config_file=my_config_file)
# or
#session = wapi.Session(client_id='client id', client_secret='client secret')
############################################

# Define curve name to read, in this example it is the wind production forecast based on
# the ec00 weather model.
curve_name = 'pro de wnd ec00 mwh/h cet min15 f'

# get the curve
curve = session.get_curve(name=curve_name)

# An INSTANCE curve contains a timeseries for each defined issue date.
# Specify the first issue_date:
# The issue_date_from specifies the first issue_date for which the relative forecast
# should be fetched. In the case of the wind production forecast, a new issue is added
# daily. The issue_date of the specific day is always set to midnight of that day.
issue_date_from = pd.Timestamp(year=2019, month=10, day=10, hour=0, tz='CET')

# Specify the last issue_date:
# The relative forecast will end before the last specified issue_date. 
issue_date_to = pd.Timestamp(year=2019, month=10, day=14, hour=0, tz='CET')

# Specify the offset:
# For each instance, a subset of the time series starting at the issue_date plus the
# data_offset is selected.
# as ISO 8601 duration (here: 6 hours)
data_offset = 'PT6H0M0S'

# Specify the max_length:
# For each instance, the selected timeseries ends after the data_max_length or when the
# following instance starts(plus data_offset).
# as ISO 8601 duration (here: 6 hours)
data_max_length = 'PT6H0M0S'

# Fetch relative forecast:
relative_forecast_wapi = curve.get_relative(data_offset=data_offset, data_max_length=data_max_length, 
                                            issue_date_from=issue_date_from, issue_date_to=issue_date_to)

# convert to pandas.Series object
relative_forecast = relative_forecast_wapi.to_pandas()

# Every day around 6 in the morning a new forecast is released that extends several days into the future. 
# The relative forecast can be applied to track the wind power production forecast based on the most 
# recent results of the ec00 weather model. In this example, an offset of 6 hours and a max_length of 6 
# hours are specified. This means that the data consists of slices for every issue_date that start 6 hours 
# after the issue_date and end 6 hours later.


# Plot curve using the integrated plot function of pandas.
relative_forecast.plot(color='blue')

# Show the figure.
plt.ylabel('MWh/h')
plt.xlabel('Time')
plt.show()
