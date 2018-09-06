"""
This simple example reads filtered data from an TIME_SERIES curve
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

# Create an empty pandas DataFrame to put all curves together
data = pd.DataFrame()

## No Filter
# read curve data from start_date to end_date to ts object
ts15min = curve.get_data(data_from=start_date, data_to=end_date)
# convert to pandas.Series object
data['no filter'] = ts15min.to_pandas()

## Filter Peak Values
# read curve data from start_date to end_date to ts object and 
# aggregate to hourly frequency
tspeak = curve.get_data(data_from=start_date, data_to=end_date, filter='PEAK')
# convert to pandas.Series object
data['peak'] = tspeak.to_pandas()

## Filter OFF-Peak Values
# read curve data from start_date to end_date to ts object and 
# aggregate to hourly frequency
tsoffpeak = curve.get_data(data_from=start_date, data_to=end_date,
                           filter='OFFPEAK')
# convert to pandas.Series object
data['offpeak'] = tsoffpeak.to_pandas()

# plot curve using matplotlib
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(data['no filter'], label='no filter', lw=2)
ax.plot(data['peak'], label='peak', linestyle='--')
ax.plot(data['offpeak'], label='offpeak', linestyle='--')
ax.legend()

# show the figure
plt.show()
