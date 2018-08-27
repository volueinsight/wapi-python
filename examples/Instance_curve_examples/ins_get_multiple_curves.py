"""
Example that reads data from wapi INSTANCE curves
can read multiple instances between two dates, saves each instance in seperate 
csv file as well as all instances to one csv file. 
Multiple curves and multiple regions (for all curves) can be specified
"""

import wapi
import pandas as pd
import os


## INPUTS
################################################
# Insert the path to your config file here!
config_file = r'C:\Users\databay\OneDrive - Wattsight\Software\wapi\wapi.ini'

# curve names to read, in this case EC00 price and PV forecasts
curve_names = ['pri {region} spot ec00 €/mwh cet h f',
               'pro {region} spv ec00 mwh/h cet min15 f']
               
# regions to read INSTANCE curves
regions = ['de', 'no1']

# end of timerange to consider issue dates (Excluded!), here we consider all
# issues until now
date_to = pd.Timestamp.now(tz='UTC').floor('H')

# Start of timerange to consider issue dates, here we consider all issues 
# from 10 days before now
date_from = date_to - pd.Timedelta(days=10)

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
    
    # iterate regions
    for region in regions:
        # create curve name to read
        cname = curve_name.format(region=region)
        
        # make subdirectory to save csv files
        dir_name = cname.replace('/','-').replace(' ','_')
        dir = os.path.join(data_dir, dir_name)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        
        # get data from curve
        print('Fetching curve', cname)
        curve = session.get_curve(name=cname)
        instances = curve.search_instances(issue_date_from=date_from, 
                                           issue_date_to=date_to,
                                           with_data=True)
                                           
        # create empty data dataframe for storing all instances                                  
        data = pd.DataFrame()
        
        # looping through instances
        for inst in instances:

            # get every instance and convert to pandas Series
            s = inst.to_pandas()
            
            # get issue date
            issue_date = pd.Timestamp(inst.issue_date).strftime('%Y%m%d%H%M')
            
            # add series to data df
            s.name = issue_date
            data = pd.concat([data,s], axis=1)
            
            # create names for single instance csv files
            csv_name = dir_name + '_' + issue_date
            # save to comma separated csv with point as decimal separator 
            s.to_csv(os.path.join(dir,csv_name+'.csv'))
            # save to semicolon separated csv with comma as decimal separator 
            s.to_csv(os.path.join(dir,csv_name+'_comma.csv'),
                     sep=';', decimal=',')     
        
        # save dataframe with all instances to csv
        data = data.sort_index(axis=1)
        data.to_csv(os.path.join(data_dir,dir_name+'.csv'))
        
            
print('[Done]')
 