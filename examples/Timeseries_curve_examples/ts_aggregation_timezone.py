"""
This simple example aggregates data from an TIME_SERIES curve and
shows how this is influenced by changing the timezone 
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

# Define start and end time
# start_date
start_date = pd.Timestamp('2018-6-1 00:00')
# end_date
end_date =  pd.Timestamp('2018-6-8 00:00')
  
# define curve name to read, in this case temperature for Germany
curve_name = 'tt de con °c cet min15 s'
# get the curve
curve = session.get_curve(name=curve_name)


## Daily average aggregation without changing the timezone
# read curve data from start_date to end_date to ts object and 
# aggregate to daily average without changing the timezone
ts1d = curve.get_data(data_from=start_date, data_to=end_date, function='AVERAGE',
                    frequency='D')
# convert to pandas.Series object
s1d = ts1d.to_pandas()

## Daily average aggregation, change timezone to UTC before aggregating
# read curve data from start_date to end_date to ts object and 
# aggregate to daily average without changing the timezone
ts1dutc = curve.get_data(data_from=start_date, data_to=end_date, function='AVERAGE',
                    frequency='D', time_zone='UTC')
# convert to pandas.Series object
s1dutc = ts1dutc.to_pandas()


# plot curves using matplotlib
fig = plt.figure()
ax = fig.add_subplot(111)
ax.step(s1d.index, s1d.values, label='Keep timezone', where='post',)
ax.step(s1dutc.index, s1dutc.values, label='Change to UTC before aggregation',
        where='post', linestyle=':')

# add legend
ax.legend()

# show the figure
plt.show()
