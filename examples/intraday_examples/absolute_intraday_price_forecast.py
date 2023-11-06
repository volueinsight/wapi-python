"""
This example fetches an absolute forecast from a TAGGED_INSTANCE curve that contains our intraday price forecast.
The absolute forecast follows updates of our intraday price forecast for a specific hourly contract.
Have a look at the documentation for further information:
https://wattsight-wapi-python.readthedocs-hosted.com/en/latest/
"""

import wapi
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
# Specify the contract_start_time:
# In the example of the intraday price forecast, the issue_date defines the point
# in time for which the forecast was made. For the intraday price a new forecast
# is released every 5 minutes. Therefore, there is a new issue every 5 minutes.
# The absolute forecast, follows all 5 minute updates for a specific hourly contract. 
# in UTC
contract_start_time='2019-11-15T18:00:00Z'

# Specify the first issue date:
# The absolute forecast will start at the first selected issue date. For our hourly
# intraday price forecast, the first forecast is published 8 hours before the start
# time of the contract.
# in UTC
issue_date_from='2019-11-15T10:00:00Z'

# Specify the tag:
# The tag defines the target period. At the moment only '90-30' is available for
# the intraday price forecast.
tag='90-30'

# Fetch absolute forecast:
# In the case of hourly intraday price forecasts, data_date is the contract_start_time. Since a new forecast
# (new issue) is released every 5 minutes the issue_frequency is 5 minutes. The issue_date_to parameter is set
# to stop fetching data after the start of the hourly contract.
absolute_forecast_wapi = curve.get_absolute(tag=tag, data_date=contract_start_time, issue_frequency='MIN5',
                                            issue_date_from=issue_date_from, issue_date_to=contract_start_time)

# convert to pandas.Series object
absolute_forecast = absolute_forecast_wapi.to_pandas()

# The fetched data contains our price forecast made for a specified hourly contract.
# Here it is 2019-11-15T19:00:00+01:00. (CET)
# The index of the pandas.Series provides the time at which the forecast for the contract 
# was updated. Numeric values are our price prognosis.

# The name of the pandas.Series includes the point of time the forecast was made.
print('Name of the pandas.Series containing the tag: {}'.format(absolute_forecast.name))

# Plot curve using the integrated plot function of pandas.
absolute_forecast.plot(color='blue', marker='o')

# Show the figure.
plt.ylabel('Price/€')
plt.xlabel('Time')
plt.show()
