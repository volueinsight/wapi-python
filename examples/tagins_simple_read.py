"""
This simple example reads data from an TAGGED_INSTANCE curve
Have a look at the documentation for further information:
XXXXXXXXXXXXXXXXXxx
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

# Get the available tags for this curve and print them
# An ensamble usually contains 51 variations of a forecast and their average
# Each of this forecasts is tagged with a number from '01' to '51'
# while the average is tagged with 'Avg'
tags = curve.get_tags()
print('\n###\nAvailable tags for this curve:\n', tags)

# One time series in a TAGED_INSTANCE cure is defined by its tag and
# the issue date (of the forecast)
# read curve data with issue date 01.01.2018 00:00 and tag='Avg'
issue_date = pd.Timestamp('2018-1-1 00:00')
ts = curve.get_instance(issue_date=issue_date, tag='Avg')
# convert to pandas.Series object
pv_actuals = ts.to_pandas()


# plot curve using the integrated plot function of pandas
pv_actuals.plot()
# show the figure
plt.show()
