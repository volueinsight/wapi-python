"""
This simple example reads the latest instances from an TAGGED_INSTANCE curve
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

  
# define curve name to read, in this case the ensamble forecast  
# of the temperature for Germany
curve_name = 'tt de con ec00ens °c cet min15 f'
# get the curve
curve = session.get_curve(name=curve_name)

# One time series in a TAGED_INSTANCE cure is defined by its tag and
# the issue date (of the forecast)
# we want to get the latest instance from this curve. The get_latest() function
# will always return ONE TS object of the latest instance, even if we provide
# a list of multiple tags to the "tags" argument. If multiple tags are provided
# it can not be assured which tag will be returned. So we strongly recommend
# only specifying ONE SINGLE TAG!
# Here we want to get the curve with the latest issue date and tag = "03"
ts = curve.get_latest(tags='03')
# convert TS object to pandas Series
latest = ts.to_pandas()
                                
# We can also specify a time limit to get the latest issue before this time
# In this case we set the time limit to yesterday 00:00
issue_date_to = pd.Timestamp.now().floor('D') - pd.Timedelta(days=1)
ts_with_limit = curve.get_latest(tags='03', issue_date_to=issue_date_to)
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
