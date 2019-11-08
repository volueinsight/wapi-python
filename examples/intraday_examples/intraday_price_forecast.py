"""
This simple example reads data from a TAGGED_INSTANCE curve that contains our 
intraday price forecast. Have a look at the documentation for further information:
https://wattsight-wapi-python.readthedocs-hosted.com/en/latest/
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

# Define curve name to read, in this case the intraday price forecast.
curve_name = 'pri de intraday €/mwh cet h f'

# get the curve
curve = session.get_curve(name=curve_name)

# An INSTANCE curve contains a timeseries for each defined issue date.
# Specify the issue_date:
# In the example of the intraday price forecast, the issue_date defines the point 
# in time for which the forecast was made. For the intraday price a new forecast 
# is released every 5 minutes. Therefore, there is a new issue every 5 minutes.
issue_date = pd.Timestamp(year=2019, month=11, day=8, hour=6, minute=45, tz='CET')

# Specify the tag:
# The tag defines the target period. At the moment only '90-30' is available for 
# the intraday price forecast.
tag='90-30'

# Fetch data for a specific issue.
intraday_price_forecast_wapi = curve.get_instance(tag=tag, issue_date=issue_date)

# convert to pandas.Series object
intraday_price_forecast = intraday_price_forecast_wapi.to_pandas()

# The fetched data contains our price forecast made at the specified point in time.
# Here it is 2019-11-08T06:45:00+01:00.
# The index of the pandas.Series provides the start time of the contract while the 
# numeric value is our price prognosis.

# Plot curve using the integrated plot function of pandas.
intraday_price_forecast.plot(color='green', marker='o', label='2019-11-08 - 6:45:00')

# It is also possible to fetch the latest forecast directly without specifying the 
# issue_date.

# Fetch data for the latest issue date. Rember to get the curve first.
latest_intraday_price_forecast_wapi = curve.get_latest(tags=tag)

# convert to pandas.Series object
intraday_price_forecast = intraday_price_forecast_wapi.to_pandas()

# The fetched data contains our latest price forecast for the intraday market.

# Plot curve using the integrated plot function of pandas.
latest_intraday_price_forecast.plot(color='blue', marker='o', label='latest')

# The name of the pandas.Series includes the point of time the forecast was made.
print('Name of the pandas.Series containing the issue_date: {}'.format(
latest_intraday_price_forecast.name))

# Show the figure.
plt.ylabel('Price/€')
plt.xlabel('Time')
plt.legend()
plt.show()
