"""
This simple example reads the latest instance from an INSTANCE curve
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

  
# define curve name to read, in this case temperature forecast for Germany
curve_name = 'tt de con ec00 °c cet min15 f'
# get the curve
curve = session.get_curve(name=curve_name)

# An INSTANCE curve contains a timeseries for each defined issue date  
# we want to get the latest instance from this curve
ts = curve.get_latest()
# convert TS object to pandas Series
latest = ts.to_pandas()


# We can also specify a time limit to get the latest issue before this time
# In this case we set the time limit to yesterday 00:00
issue_date_to = pd.Timestamp.now().floor('D') - pd.Timedelta(days=1)
ts_with_limit = curve.get_latest(issue_date_to=issue_date_to)
# convert TS object to pandas Series
latest_with_limit = ts_with_limit.to_pandas()


# plot both timeseries with matplotlib
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(latest, label='latest')
ax.plot(latest_with_limit, label='latest_with_limit')
# add a legend
ax.legend()
# show the figure
plt.show()
