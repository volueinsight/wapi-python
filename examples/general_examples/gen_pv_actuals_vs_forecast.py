"""
This simple example compares yesterday's Photovoltaic Forecast based on the EC00
weather forecast and the GFS00 weather forecasts with the Actual PV production.
The comparison can be performed for any region
"""

import wapi
import pandas as pd
import matplotlib.pyplot as plt

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################
# Select a valid region (you have access to)
region = 'de'
############################################

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# Define yesterday
yesterday = pd.Timestamp.now().floor('D') - pd.Timedelta(days=1)

## Get PV actuals
# define curve name using the specified region
curve_name = 'pro ' + region + ' spv mwh/h cet min15 a'
# get the curve
curve_pv = session.get_curve(name=curve_name)
# get actual data since yesterday
ts_pv = curve_pv.get_data(data_from=yesterday)
# convert to pandas Series
pv = ts_pv.to_pandas()

## Get EC00 PV forecast data
# define curve name using the specified region
curve_name = 'pro ' + region + ' spv ec00 mwh/h cet min15 f'
# get the curve
curve_ec00 = session.get_curve(name=curve_name)
# get ec00 forecast with issue_date yesterday 00:00
ts_ec00 = curve_ec00.get_instance(issue_date=yesterday)
# convert to pandas Series
ec00 = ts_ec00.to_pandas()
# only keep same time index as available actuals to compare
ec00 = ec00.loc[pv.index]


# GFS00 PV forecast
# define curve name using the specified region
curve_name = 'pro ' + region + ' spv gfs00 mwh/h cet min15 f'
# get the curve
curve_gfs00 = session.get_curve(name=curve_name)
# get gfs forecast with issue_date yesterday 00:00
ts_gfs00 = curve_gfs00.get_instance(issue_date=yesterday)
# convert to pandas Series
gfs00 = ts_gfs00.to_pandas()
# only keep same time index as available actuals to compare
gfs00 = gfs00.loc[pv.index]


## plot forecasts vs actuals
fig = plt.figure()
ax = fig.add_subplot(211)
ax.plot(ec00, label='EC00 Forecast', color='b')
ax.plot(gfs00, label='GFS00 Forecast', color='g')
ax.plot(pv, label='PV Production '+region, color='r')
ax.legend()

## calculate and plot mean absolute error of forecasts
ax2 = fig.add_subplot(212)
mae_ec00 = np.mean(np.abs(pv.values - ec00.values))
mae_gfs00 = np.mean(np.abs(pv.values - gfs00.values))
ax2.bar(1,mae_ec00, color='b')
ax2.bar(2,mae_gfs00, color='g')
ax2.set_xticks([1, 2])
ax2.set_xticklabels(['ec00', 'gfs00'])
ax2.set_ylabel('mean absolute eroor (MWh/h)')

# show the figure
plt.show()
