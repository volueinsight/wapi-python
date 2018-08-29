"""
This simple example reads data for multiple tags from an TAGGED_INSTANCE curve
Have a look at the documentation for further information:
https://wattsight-wapi-python.readthedocs-hosted.com/en/latest/index.html
"""

import wapi
import pandas as pd
import matplotlib.pyplot as plt

############################################
# Insert the path to your config file here!
my_config_file = r'C:\Users\databay\OneDrive - Wattsight\Software\wapi\wapi.ini'
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
# you can define multiple tags using the get_instance method
# the function will then return a list of TS objects
# read curve data with issue date 01.01.2018 00:00 and tags=['Avg','01','12']
tags = ['Avg','01','12']
issue_date = pd.Timestamp('2018-7-1 00:00')
ts_list = curve.get_instance(issue_date=issue_date, tag=tags)

# create a matplotlib figure and axis
fig = plt.figure()
ax = fig.add_subplot(111)

# loop through the list of TS objects
for ts in ts_list:
    # convert to pandas.Series object
    s = ts.to_pandas()
    # plot timeseries and choose tag as label
    ax.plot(s, label=ts.tag)
    
# create a legend for the plot
ax.legend()
# show the figure
plt.show()
