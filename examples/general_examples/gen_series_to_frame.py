"""
This example shows how to join multiple pandas Series to a DataFrame
For further information take a look at the pandas documentation:
https://pandas.pydata.org/pandas-docs/stable/merging.html
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

## Combine Series with same time index
######################################

# To combine pandas Series that all have the same time index, the simplest
# option is to add a new column for every series
# We first create an empty dataframe
df1 = pd.DataFrame()

# now we read temperature data for 3 different regions for the same time horizon
regions = ['fr','es','de']
# start_date
start_date = pd.Timestamp('2018-6-1 00:00')
# end_date
end_date =  pd.Timestamp('2018-6-8 00:00')
# we loop through the regions and get the data for each region
for r in regions:
    # define curve name to read, based on the region
    curve_name = 'tt ' + r + ' con °c cet min15 s'
    # get the curve
    curve = session.get_curve(name=curve_name)
    # read curve data from start_date to end_date to ts object
    ts = curve.get_data(data_from=start_date, data_to=end_date)
    # convert to pandas.Series object
    s = ts.to_pandas()
    # add the series as a new column to the DataFrame, set the region as name
    df1[r] = s

# plot the dataframe using the plotting function from pandas
df1.plot()


### Combine Series with different time index
############################################

# To combine pandas Series that all have the same time index, is a bit more
# complicated and there are mulriple options. Here we use the pandas.concat()
# function
# We first create an empty dataframe
df2 = pd.DataFrame()

# now we read temperature forecasts of germany for 3 different issue dates
# we create the issue_dates, yesterday, plus 1 and 2 days before yesterday
yesterday = pd.Timestamp.now().floor('D') - pd.Timedelta(days=1)
yesterday_1before = yesterday - pd.Timedelta(days=1)
yesterday_2before = yesterday - pd.Timedelta(days=2)
# put them together in a list
issue_dates = [yesterday, yesterday_1before, yesterday_2before]

# define curve name to read, in this case temperature forecast for Germany
curve_name = 'tt de con ec00 °c cet min15 f'
# get the curve
curve = session.get_curve(name=curve_name)

# we loop through the issue_dates and get the forecast data for each
for issue_date in issue_dates:
    # read curve data for this issue_date
    ts = curve.get_instance(issue_date=issue_date)
    # convert to pandas.Series object
    s = ts.to_pandas()
    # use the pandas.concat() function to add a new column and keep all indexes
    df2 = pd.concat([df2,s], axis=1)

# plot the dataframe using the plotting function from pandas
df2.plot()


# show the figures
plt.show()
