"""
This simple example reads data from an INSTANCE curve
Have a look at the documentation for further information:
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
# read timeseries data with issue date 01.01.2018 00:00
issue_date = pd.Timestamp('2018-1-1 00:00')
ts = curve.get_instance(issue_date=issue_date)
# convert to pandas.Series object
s = ts.to_pandas()


# plot curve using the integrated plot function of pandas
s.plot()
# show the figure
plt.show()
