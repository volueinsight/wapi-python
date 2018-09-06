"""
This simple example reads data for multiple instances from an TAGGED_INSTANCE curve
Have a look at the documentation for further information:
https://wattsight-wapi-python.readthedocs-hosted.com/en/latest/index.html
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

  
# define curve name to read, in this case the ensamble forecast  
# of the temperature for Germany
curve_name = 'tt de con ec00ens °c cet min15 f'
# get the curve
curve = session.get_curve(name=curve_name)

# One time series in a TAGED_INSTANCE cure is defined by its tag and
# the issue date (of the forecast)
# we want to get all instances with a issue date between a given timerange
# Setting with_data argument to True, ensures that do not only read meta data
# here we don't provide the "tags" argument, so that by default we get all
# available tags for each found instance. We could also limit the curves
# we get by providing list of tags or a single tag with the "tags" argument
issue_date_from = pd.Timestamp('2018-7-1 00:00')
issue_date_to = pd.Timestamp('2018-7-4 00:00')
ts_list = curve.search_instances(issue_date_from=issue_date_from,
                                 issue_date_to=issue_date_to,
                                 with_data=True)
                                
# Since we have too many curves to plot them all, we only want to plot the
# curves with tag='01' now. Therefore we loop through all TS objects
# But first we create a figure and axis to plot
fig = plt.figure()
ax = fig.add_subplot(111)
for ts in ts_list:
    # print the tag and issue date of all curves to the console
    print('Curve with tag: "'+ts.tag+'" and issue date: '+ts.issue_date)

    if ts.tag == '01':
        # if the tag of the cuvee is "01", we convert it to a pandas Series
        s = ts.to_pandas()
        # and plot it
        ax.plot(s, label=ts.tag+' - '+ts.issue_date)
# add a legend to the plot
ax.legend()


# As described before, we can limit the returned curves by specifying a list 
# of tags or a single tag to consider. So in this case we try to reproduce
# the plot by only getting the curves we actually want to plot
ts_list_limit = curve.search_instances(issue_date_from=issue_date_from,
                                       issue_date_to=issue_date_to,
                                       with_data=True,
                                       tags = '01')

# Now we plot all curves we got. We create a new figure and axis to plot first.
fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
# Now we loop through the TS objects and plot them
for ts in ts_list_limit:
    # convert TS object to pandas Series
    s = ts.to_pandas()
    # plot it
    ax2.plot(s, label=ts.tag+' - '+ts.issue_date)
# add a legend to the plot
ax2.legend()

# show the figures
plt.show()