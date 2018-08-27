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


## Hourly average aggregation
# read curve data from start_date to end_date to ts object and 
# aggregate to hourly frequency
ts1h = curve.get_data(data_from=start_date, data_to=end_date,
                      function='average', frequency='H', output_time_zone='UTC')
# convert to pandas.Series object
s1h = ts1h.to_pandas()