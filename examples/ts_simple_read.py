"""
This simple example reads data from an TIME_SERIES curve
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

# Define start and end time
# start_date
start_date = pd.Timestamp('2018-6-1 00:00')
# end_date
end_date =  pd.Timestamp('2018-6-8 00:00')
  
# define curve name to read, in this case temperature for Germany
curve_name = 'tt de con °c cet min15 s'
# get the curve
curve = session.get_curve(name=curve_name)
# read curve data from start_date to end_date to ts object
ts = curve.get_data(data_from=start_date, data_to=end_date)
# convert to pandas.Series object
s = ts.to_pandas()


# plot curve using the integrated plot function of pandas
s.plot()
# show the figure
plt.show()
