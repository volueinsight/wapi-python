"""
Example that reads data from wapi TIMESERIES curves
can read multiple curves, and each curve for multiple regions
aggregates (averages) output frequency, if specified.
Save read data to csv files.
"""

import wapi
import pandas as pd
import os

################################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
################################################


# curve names to read (in this case temperature and PV production actuals)
curve_names = ['tt {region} con °c cet {freq} s',
               'pro {region} spv mwh/h cet {freq} a']

#define frequency for every curve as in curve name
freqs_curve = ['min15'] * len(curve_names)

# desired freq of output, define for every curve
freqs_out = ['H'] * len(curve_names)

# Regions to read TIMESERIES curves
regions = ['DE', 'ES', 'FR']

# Start Date of data
start = pd.Timestamp('2018-01-01 00:00')

# End date of data (last date is EXCLUDED!)
end = pd.Timestamp('2018-07-01 00:00')
################################################

# make data directory in the folder where this file is, if it does not exist
# Get the path of the directory where this file is
file_dir = os.path.dirname(os.path.realpath(__file__))
# Check if there is a "data" folder in this directory
data_dir = os.path.join(file_dir,'data')
if not os.path.isdir(data_dir):
    # if not, create one
    os.mkdir(data_dir)

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=config_file)

# loop through the given curves
for c, curve_name in enumerate(curve_names):
    # init empty df for each curve
    df = pd.DataFrame()
    # get curve and output frequency for curve name
    freq_curve = freqs_curve[c]
    freq_out = freqs_out[c]

    # iterate regions
    for region in regions:
        # get curve data and convert to pandas Series
        cname = curve_name.format(region=region, freq=freq_curve)
        print('Fetching curve', cname)
        curve = session.get_curve(name=cname)
        ts = curve.get_data(data_from=start, data_to=end)
        s = ts.to_pandas()

        if freq_curve != freq_out:
            # convert frequency if needed
            s = s.groupby(pd.Grouper(freq=freq_out)).mean()

        # add data to curve dataframe
        df[curve_name.format(region=region, freq=freq_out)] = s

    # create valid name for saving to csv
    csv_name = curve_name.format(region='', freq=freq_out)
    csv_name = csv_name.replace('/','-')
    csv_name = csv_name.replace('  ',' ')
    csv_name = csv_name.replace(' ','_')

    # save to comma separated csv with point as decimal separator
    df.to_csv(os.path.join('data',csv_name+'.csv'))
    # save to semicolon separated csv with comma as decimal separator
    df.to_csv(os.path.join('data',csv_name+'_comma.csv'), sep=';', decimal=',')
print('[Done]')
