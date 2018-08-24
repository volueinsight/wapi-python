"""
This example shows how to reproduce the plot from these 4 pages:
Consumption: https://app.wattsight.com/#tab/power/115/2
Photovoltaic Load: https://app.wattsight.com/#tab/power/135/2
Wind: https://app.wattsight.com/#tab/power/126/2
Residual Load: https://app.wattsight.com/#tab/power/109/2

The pages show the latest forecasts compared to actual values and normals
"""

import wapi
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

## INPUTS
############################################
# Insert the path to your config file here!
my_config_file = r'C:\Users\databay\OneDrive - Wattsight\Software\wapi\wapi.ini'

# Choose one of the available regions by using its abbreviation
# as shown on the top of each wattsight page 
# (eg https://app.wattsight.com/#tab/power/135/2)
region = 'de' 

# choose one of the four possible categories for this plot:
# 'con' for Consumption
# 'wnd' for Wind Power
# 'spv' for Solar Photovoltaic
# 'rdl' for Residual Load
category = 'con'

# Set the aggregation function ['average','sum'] and output frequency of the
# aggregation. The frequency string consists of a letter defining the time unit
# followed by an integer defining the multiple of this unit.
# eg the letter 'H' means "hour", so 'H' or 'H1' defines
# an aggregation frequency of "1 hour", where 'H6' stands for 
# "6 hours" and 'H12' for "12 hours". The following letter<->unit 
# definitions are valid
# * 'Y': year
# * 'M': month
# * 'W': week
# * 'D': day
# * 'H': hour
# * 'MIN': minutes
# If you want to keep the original 15 minute resolution, set both to None!
freq = 'H'
func = 'average'

############################################


###############
## Get the data
###############

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# get current dates and timeranges to get data
now = pd.Timestamp.now()
today = now.floor('D')
yesterday = today - pd.Timedelta(days=1)
end = today + pd.Timedelta(days=10)

# create the first part of the curve name dependent on the category and region
if category == 'con':
    curve_part1 = 'con ' + region
elif category == 'rdl':
    curve_part1 = 'rdl ' + region
else:
    curve_part1 = 'pro ' + region + ' ' + category

# specifiy timezone based on region
if region == 'tr':
    # Turkey has timezone TRT
    tz = 'trt'
else:
    # All other regions ahve timezone CET
    tz = 'cet'

# get normal data
curve_normal = session.get_curve(name=curve_part1+' mwh/h '+tz+' min15 n')
normal = curve_normal.get_data(data_from=yesterday, data_to=end,
                               function=func, frequency=freq)
normal = normal.to_pandas(name='Normal')/1000

# get most recent actual data
curve_actual = session.get_curve(name=curve_part1+' mwh/h '+tz+' min15 a')
actual = curve_actual.get_data(data_from=yesterday, function=func,
                               frequency=freq)
actual = actual.to_pandas(name='Actual')/1000

# get backcast for last day
curve_actual = session.get_curve(name=curve_part1+' mwh/h '+tz+' min15 s')
backcast = curve_actual.get_data(data_from=yesterday, data_to=today,
                                 function=func, frequency=freq)
backcast = backcast.to_pandas(name='Backcast')/1000


# The EC Forecasts are published the following order:
# ... EC00, EC00Ens, EC12, EC12Ens, EC00, EC00Ens, EC12, EC12Ens, ...t
# We want to plot the latest three forecasts, so we first read the latest 
# issued version of each forecast together with its issue date

# get EC00 data and issue date
curve_EC00 = session.get_curve(name=curve_part1+' ec00 mwh/h '+tz+' min15 f')
EC00 = curve_EC00.get_latest(function=func, frequency=freq)
EC00_idate = EC00.issue_date
# Convert issue date to CET make it a string again
EC00_idate = pd.Timestamp(EC00_idate).tz_convert('CET').strftime('%Y-%m-%d')
EC00 = EC00.to_pandas(name='EC00 ' + EC00_idate[8:10] + '.' + EC00_idate[5:7])
EC00 = EC00.loc[today:end]/1000

# get EC12 data and issue date
curve_EC12 = session.get_curve(name=curve_part1+' ec12 mwh/h '+tz+' min15 f')
EC12 = curve_EC12.get_latest(function=func, frequency=freq)
EC12_idate = EC12.issue_date
# Convert issue date to CET make it a string again
EC12_idate = pd.Timestamp(EC12_idate).tz_convert('CET').strftime('%Y-%m-%d')
EC12 = EC12.to_pandas(name='EC12 ' + EC12_idate[8:10] + '.' + EC12_idate[5:7])
EC12 = EC12.loc[today:end]/1000

# get EC00Ens data and issue date
curve_EC00Ens = session.get_curve(name=curve_part1+' ec00ens mwh/h '+tz+' min15 f')
EC00Ens_idate = curve_EC00Ens.get_latest(with_data=False).issue_date
EC00Ens_tslist = curve_EC00Ens.get_instance(EC00Ens_idate, function=func, 
                                            frequency=freq)
# Convert issue date to CET make it a string again
EC00Ens_idate = pd.Timestamp(EC00Ens_idate).tz_convert('CET').strftime('%Y-%m-%d')
if EC00Ens_tslist is None:
    # while the EC00ENS forecast is processed, get_latest() function can already
    # return valid values (the average of the ensamble) with an issue date,
    # while the get_instance() function returns None, since not all data
    # is available yet. In this case we set the issue date to "2017-01-01" and 
    # ignore the EC00ENS, since then it is the oldest forecast we will not 
    # consider further.
    EC00Ens_idate = '2017-01-01'
else:
    for i,ts in enumerate(EC00Ens_tslist):
        if i==0:
            EC00Ens = ts.to_pandas(name='EC00Ens_'+ts.tag).to_frame()
        else:
            EC00Ens['EC00Ens_'+ts.tag] = ts.to_pandas()
    EC00Ens = EC00Ens.loc[today:end]/1000
    EC00Ens_avg = EC00Ens['EC00Ens_Avg']
    EC00Ens_avg.name = 'EC00Ens ' + EC00Ens_idate[8:10] + '.' + EC00Ens_idate[5:7]
    
# get EC12Ens data and issue date  
curve_EC12Ens = session.get_curve(name=curve_part1+' ec12ens mwh/h '+tz+' min15 f')
EC12Ens_idate = curve_EC12Ens.get_latest(with_data=False).issue_date
EC12Ens_tslist = curve_EC12Ens.get_instance(EC12Ens_idate, function=func, 
                                            frequency=freq)
# Convert issue date to CET make it a string again
EC12Ens_idate = pd.Timestamp(EC12Ens_idate).tz_convert('CET').strftime('%Y-%m-%d')
if EC12Ens_tslist is None:
    # while the EC12ENS forecast is processed, get_latest() function can already
    # return valid values (the average of the ensamble) with an issue date,
    # while the get_instance() function returns None, since not all data
    # is available yet. In this case we set the issue date to "2017-01-01" and 
    # ignore the EC12ENS, since then it is the oldest forecast we will not 
    # consider further.
    EC12Ens_idate = '2017-01-01'
else:
    for i,ts in enumerate(EC12Ens_tslist):
        if i==0:
            EC12Ens = ts.to_pandas(name='EC12Ens_'+ts.tag).to_frame()
        else:
            EC12Ens['EC12Ens_'+ts.tag] = ts.to_pandas()
    EC12Ens = EC12Ens.loc[today:end]/1000
    EC12Ens_avg = EC12Ens['EC12Ens_Avg']
    EC12Ens_avg.name = 'EC12ENS ' + EC12Ens_idate[8:10] + '.' + EC12Ens_idate[5:7]


##########################################
# find out the time order of the forecasts
##########################################  

# which forecast is newer?
if EC00_idate > EC00Ens_idate:
   # EC00 is the latest available forecast!
   last_ens = EC12Ens
   fc_order = [EC12, EC12Ens_avg, EC00]
elif EC00Ens_idate >= EC12_idate:
   # EC00ENS is the latest available forecast!
   last_ens = EC00Ens
   fc_order = [EC12Ens_avg, EC00, EC00Ens_avg]
elif EC12_idate >= EC00Ens_idate:
   # EC12 is the latest available forecast!
   last_ens = EC00Ens
   fc_order = [EC00, EC00Ens_avg, EC12]
else:
   # EC12ENS is the latest available forecast!
   last_ens = EC12Ens
   fc_order = [EC00Ens_avg, EC12, EC12Ens_avg]
        
        
##################
## Plot the curves
##################  
      
# Create figure and subplots
fig = plt.figure(figsize=[16,9])
gs = mpl.gridspec.GridSpec(4, 1, height_ratios=[1,0.5,0.5,0.1])
ax0 = fig.add_subplot(gs[0])
ax1 = fig.add_subplot(gs[1], sharex=ax0)
ax2 = fig.add_subplot(gs[2], sharex=ax0)
ax3 = fig.add_subplot(gs[3]) # axes subplot for legend

# some layout settings
colors = ['brown','blue','red']
lw = 2 #linewidth
fs=16 # font size
ms = 6 # marker size

# Title
fig.suptitle(curve_part1, fontsize=fs)

# first subplot
###############

# plot ensambles
for c in last_ens.columns[2:]:
    ax0.plot(last_ens.index, last_ens[c].values, color='lightblue', lw=1)
# the first ensamble curve is supposed to be the most likely one and therefore
# is plotted with a slightly different color
c = last_ens.columns[1]
ax0.plot(last_ens.index, last_ens[c].values, color='steelblue', lw=1)

# plot normal
ax0.plot(normal, color='khaki', label='Normal', lw=lw)
# plot backcast
ax0.plot(backcast, color='darkgrey', label='Backcast', lw=lw)

# plot forecasts in right order
for i, fc in enumerate(fc_order):
    ax0.plot(fc, color= colors[i], label = fc.name, lw=lw)
ax0.plot(actual, color='black', label='Actual', marker='.', markersize=ms, lw=lw)

# set axis parameters
plt.setp(ax0.get_xticklabels(), visible=False)
ax0.grid()
ax0.set_ylabel('Nominal Values GWh/h', fontsize=fs)
ax0.tick_params(labelsize=fs)

# get legend handl
h0, l0 = ax0.get_legend_handles_labels()

# second subplot
################

# plot Ensamble difference to latest forecast
for c in last_ens.columns[2:]:
    # caluclate difference to ensamble average and plot it
    diff = last_ens[c] - fc_order[-1]
    ax1.plot(diff, color='lightblue', lw=1)
    
# the first ensamble curve is supposed to be the most likely one and therefore
# is plotted with a slightly different color
c = last_ens.columns[1]
diff = last_ens[c] - fc_order[-1]
ax1.plot(diff, color='steelblue', lw=1)

#plot zero line
ax1.plot(fc_order[-1]*0, color='red', lw=lw)

# set axis parameters
plt.setp(ax1.get_xticklabels(), visible=False)
ax1.grid()
ax1.set_ylabel('Spread', fontsize=fs)
ax1.tick_params(labelsize=fs)
ylim = max(np.abs(ax1.axes.get_ylim())) # max absolute y limit
ax1.set_ylim([-ylim,ylim]) # ensure same negative and positive limit

#third subplot
##############

# backcast - Actual
ax2.plot(backcast-actual, color='black', label='Backcast-Actual', marker='.', 
         markersize=ms, lw=lw)
# add latest forecast - actual
ax2.plot(fc_order[2]-actual, color='black', marker='.', 
         markersize=ms, lw=lw)

# plot latest minus second latest forecast       
ax2.plot(fc_order[2]-fc_order[1], color=colors[1], lw=lw,
         label=fc_order[0].name.split(' ')[0]+'-'+fc_order[1].name.split(' ')[0])
         
# plot second latest minus third latest forecast 
ax2.plot(fc_order[1]-fc_order[0], color=colors[0], lw=lw,
         label=fc_order[1].name.split(' ')[0]+'-'+fc_order[2].name.split(' ')[0])

# plot lates forecast minus normals         
lastfc_normal = fc_order[2]-normal
# get time resolution of data in hours to specify the bar width
hours_diff = (lastfc_normal.index[1] - lastfc_normal.index[0]).delta/36e11
ax2.bar(lastfc_normal.index, lastfc_normal.values, color='moccasin',
        width=0.04*hours_diff,
        label='Dev. '+fc_order[2].name.split(' ')[0]+'-Normal')

# set axis parameters
ax2.grid()
ax2.set_ylabel('Deviation/Shift', fontsize=fs)
ax2.tick_params(labelsize=fs)
ylim = max(np.abs(ax2.axes.get_ylim())) # max absolute y limit
ax2.set_ylim([-ylim,ylim]) # ensure same negative and positive limit

# get legend handlers
h2, l2 = ax2.get_legend_handles_labels()
         
# subplot for legends
#####################
ax3.axis('off')
# show legend for first subplot (ax0)
l0 = ax3.legend(h0[::-1], l0[::-1], ncol=6, fontsize=fs,loc='upper left', bbox_to_anchor=[0, 1.2])
# show legend for third subplot (ax2)
l2 = ax3.legend(h2, l2, ncol=6, fontsize=fs,loc='upper left', bbox_to_anchor=[0, -0.1])
ax3.add_artist(l0) # needed for having 2 legends


# make figure tight and show it
fig.tight_layout()
plt.show()