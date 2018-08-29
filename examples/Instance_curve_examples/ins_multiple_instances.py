"""
This simple example reads multiple instances from an INSTANCE curve
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

  
# define curve name to read, in this case temperature forecast for Germany
curve_name = 'tt de con ec00 °c cet min15 f'
# get the curve
curve = session.get_curve(name=curve_name)

# An INSTANCE curve contains a timeseries for each defined issue date  
# we want to get all instances with a issue date between a given timerange
# Setting with_data argument to True, ensures that do not only read meta data
# but also the data values of the curves
issue_date_from = pd.Timestamp('2018-7-1 00:00')
issue_date_to = pd.Timestamp('2018-7-4 00:00')
ts_list = curve.search_instances(issue_date_from=issue_date_from,
                                 issue_date_to=issue_date_to,
                                 with_data=True)
                            
# The function returns a list of TS objects. We want to store the data of all
# objects into one pandas DataFrame. First we create an empty DataFrame
df = pd.DataFrame()

# Now we loop through the TS objects
for ts in ts_list:
    # we convert each TS object to a pandas Series
    # We set the issue date as name of the Series
    s = ts.to_pandas(name=ts.issue_date)
     
    # Now we add the series as a new column to the pandas DataFrame
    df = pd.concat([df, s], axis=1)
    

# We can plot the data using the integrated plot function of pandas
df.plot()
# show the figure
plt.show()
