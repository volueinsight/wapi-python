"""
This example shows how to write data from a pandas Series or a pandas DataFrame
object to a csv or xlsx file. You can write pandas objects to various other
data type files. Have a look at the pandas documentation for more information
https://pandas.pydata.org/pandas-docs/stable/io.html
"""

import wapi
import pandas as pd
import matplotlib.pyplot as plt
import os

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# get the directory of the current file
file_dir = os.path.dirname(os.path.realpath(__file__))

## Combine Series to a DataFrame
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
    

### Save to csv
#########################

# The pandas.Series object "s" is the last of the 3 curves we read.
# The pandas.DataFrame object "df1" contains all 3 curves we read.

# we can simply save both objects as a csv file using the to_csv() function
# You can find more information about this function here:
# https://pandas.pydata.org/pandas-docs/stable/io.html#io-store-in-csv

# create the filenames to save the data to. In this case, we save it to 
# csv files called "series.csv" and "frame.csv" into the same folder as this 
# python script
filename_s = os.path.join(file_dir,'series.csv')
filename_df = os.path.join(file_dir,'frame.csv')

# When using to_csv, by default the csv file is comma separated with point 
# as decimal separator.
# save the series data to the csv file
s.to_csv(filename_s)
# save the dataframe data to the csv file
df1.to_csv(filename_df)

# We can also change the data separator and the decimal separator of the csv 
# file. Here we save to semicolon separated csv with comma as decimal separator
# and call the files "series_comma.csv" and "frame_comma.csv".
filename_s = os.path.join(file_dir,'series_comma.csv')
filename_df = os.path.join(file_dir,'frame_comma.csv')
# save the series data to the csv file, set data and decimal separator
s.to_csv(filename_s, sep=';', decimal=',') 
# save the dataframe data to the csv file, set data and decimal separator
df1.to_csv(filename_df, sep=';', decimal=',') 


### Save to xlsx
###########################

# The pandas.Series object "s" is the last of the 3 curves we read.
# The pandas.DataFrame object "df1" contains all 3 curves we read.

# we can simply save both objects as a xlsx file using the to_excel() function
# You can find more information about this function here:
# https://pandas.pydata.org/pandas-docs/stable/io.html#io-excel-writer

# create the filenames to save the data to. In this case, we save it to 
# xlsx files called "series.xlsx" and "frame.xlsx" into the same folder as this 
# python script
filename_s = os.path.join(file_dir,'series.xlsx')
filename_df = os.path.join(file_dir,'frame.xlsx')

# Unfortunately, excel does not support time-zone aware time information.
# Therefore we have to remove the timezone information form the index of
# the Series and DataFrame before we can save to excel. Otherwise this will
# raise an error.
# We do this by calling the tz_localize(None) method right before calling
# the to_excel function. This will remove the timezone information just for 
# this call of the to_excel method and not overwrite the Series or DataFrame
# object.
# save the series data without timezone awareness to xlsx
s.tz_localize(None).to_excel(filename_s)
# save the DataFrame data without timezone awareness to xlsx
df1.tz_localize(None).to_excel(filename_df)


## Save multiple Series/DataFrames different sheets in same xlsx
# We can also save the Series and the DataFrame (and possibly more objects)
# to different sheets of the same xlsx file

# Therefore we create a Pandas Excel writer, where we define the name and path
# of the xlsx file. Here we save the data to a file called "series_frame.xlsx" 
# which is located in the same folder as this python script
filename = os.path.join(file_dir,'series_frame.xlsx')
writer = pd.ExcelWriter(filename)

# Now we can write each dataframe/series to a different worksheet of this file,
# by using the ExcelWriter object.
df1.tz_localize(None).to_excel(writer, sheet_name='DataFrame')
s.tz_localize(None).to_excel(writer, sheet_name='Series')

# At the end we have to close the Pandas Excel writer and output the Excel file.
writer.save()

