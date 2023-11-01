"""
This example shows how to set up an event listener, so we can run some code
whenever there are changes in the defined curves.
In this case, we want to write PV and Wind actuals for the 4 German TSO'a,
France, Belgium and the two price zones in Denmark to our
database whenever there is new data.
Here our "database" is simply a csv file for each curve, where we append
the latest data.
Be aware, that it might take up to 15 minutes until there is new data in the
curves and this script actually does something
"""

import wapi
import pandas as pd
import time
import os

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

## Set up an event listener for defined curves
##############################################

# define curve names
curve_names = ['pro be spv intraday mwh/h cet min15 a',
               'pro de-50hz spv intraday mwh/h cet min15 a',
               'pro de-amp spv intraday mwh/h cet min15 a',
               'pro de-enbw spv intraday mwh/h cet min15 a',
               'pro de-ttg spv intraday mwh/h cet min15 a',
               'pro dk1 spv intraday mwh/h cet min15 a',
               'pro dk2 spv intraday mwh/h cet min15 a',
               'pro fr spv intraday mwh/h cet min15 a',
               'pro be wnd intraday mwh/h cet min15 a',
               'pro de-50hz wnd intraday mwh/h cet min15 a',
               'pro de-amp wnd intraday mwh/h cet min15 a',
               'pro de-enbw wnd intraday mwh/h cet min15 a',
               'pro de-ttg wnd intraday mwh/h cet min15 a',
               'pro dk1 wnd intraday mwh/h cet min15 a',
               'pro dk2 wnd intraday mwh/h cet min15 a',
               'pro fr wnd intraday mwh/h cet min15 a']

# search for the curves in wapi and return curve object
curves = session.search(name=curve_names)

# Set up the event listener for the curves
# We expect the curves to be updated every 15 minutes, so we set the
# timout to 15 minutes
events = session.events(curves, timeout=15*60)

# Create a "data_base" folder, where the csv files will be saved
if os.path.isdir('data_base') is False:
    os.mkdir('data_base')

# We don't want this example script to run forever, so we will stop it
# when there is a new event and the run time exceeds 1 hour
# So here we get the starting time
t_start = time.time()

# This for loop waits until there is a new event and then runs the
# code ones for each events
for e in events:

    if isinstance(e, wapi.events.EventTimeout):
        # If there is a timeout, you can handle this here, eg raise a warning
        print('TIMEOUT!')

    elif isinstance(e, wapi.events.CurveEvent):
        print('New event in curve: ' + e.curve.name)
        curve = e.curve
        # since actuals are usually a bit delayed, we get data
        # since the last 24 hours from the curve
        data_from = pd.Timestamp.now() - pd.Timedelta(hours=24)
        # get the TS object
        ts = curve.get_data(data_from=data_from)
        # convert to pandas Series
        data = ts.to_pandas()
        # get last timestep
        data_last = data.tail(1)

        # the name of the csv file for each curve is the curve name,
        # where the spaces and '/' are replaced by underscores
        csv_file = curve.name.replace(' ','_').replace('/','_')
        # we want the csv file to be in the "data_base" folder
        csv_file = os.path.join('data_base',csv_file)

        # Now write the last value to the csv file of the curve
        # To make sure we append the data, if there is an existing csv file
        # we set the mode in pandas.to_csv to "a" (=append) and we skip
        # writing the header
        data_last.to_csv(csv_file, mode='a', header=False)

    if (time.time() - t_start) > (60*60):
        # We don't want this example script to run forever, so we will stop it
        # when there is a new event and the run time exceeds 1 hour
        break
