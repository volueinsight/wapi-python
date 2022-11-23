"""
This example shows an approach to downloading many instances
in a safe but efficient way.
Typically used to download the history of forecasts.
"""

import wapi
from datetime import datetime, timedelta
from dateutil.parser import parse
from zoneinfo import ZoneInfo
import time

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# As an example, we read the temperature ensemble forecast
# for some regions for the ec00ens and ec12ens forecast of
# the consumption model.
# We download all ensembles (tags).

CET = ZoneInfo('CET')

# Just grab some possible start/end issue dates if we cannot
# find them from the curve metadata.
# At some point, we will annotate the curve objects with
# the actually available start/end issue date

#default_start_date = parse('2015-01-01T00:00+01:00').astimezone(CET)
default_start_date = CET.localize(datetime.now()) - timedelta(days=30)
default_end_date = CET.localize(datetime.now())

# There is a max number of datapoints per request, which
# is adjusted to keep things robust.  This is usually OK,
# reduce the number if you get errors.
max_datapoints = 250_000.0

regions = ['fr','es','de']
sources = ['ec00ens', 'ec12ens']

for r in regions:
    for s in sources:
        # curve name to read, based on the region and source
        curve_name = 'tt ' + r + ' con ' + s + ' °C cet min15 f'
        # get the curve
        curve = session.get_curve(name=curve_name)

        # Fetch the default tag of the latest instance to get an
        # estimate of instance size, assuming all instances are
        # similar.  Fetch the tag set.
        instance_size = len(curve.get_latest().points)
        tags = curve.get_tags()
        max_instances = int(max_datapoints / (instance_size * len(tags)))

        # Find the range of instances we want to download
        if curve.accessRange['begin'] is None:
            start_date = default_start_date
        else:
            start_date = parse(curve.accessRange['begin']).astimezone(CET)
            if start_date < default_start_date:
                start_date = default_start_date
        if curve.accessRange['end'] is None:
            end_date = default_end_date
        else:
            end_date = parse(curve.accessRange['end']).astimezone(CET)
            if end_date > default_end_date:
                end_date = default_end_date

        read_start_time = time.time()

        # First fetch the list of instances without the time series, for the default tag,
        # which is a fairly light-weight call.
        instance_list = curve.search_instances(issue_date_from=start_date, issue_date_to=end_date,
                                               tags=tags[0], with_data=False)
        instance_date_list = [i.issue_date for i in instance_list]
        instance_date_list.reverse()  # The call returns from newest to oldest.

        # Then loop over them and fetch all instances.
        total_data_points = 0
        total_instances = 0

        print("Reading {}, {} issue dates, {} tags, {} instances each call".format(
            curve_name, len(instance_date_list), len(tags), max_instances))

        for idx in range(0, len(instance_date_list), max_instances):
            start_frag = instance_date_list[idx]
            if (idx + max_instances) < len(instance_date_list):
                end_frag = instance_date_list[idx + max_instances]
            else:
                end_frag = end_date

            instances = curve.search_instances(issue_date_from=start_frag, issue_date_to=end_frag,
                                               tags=tags, with_data=True)

            # Process this list of instances
            total_instances += len(instances)
            for i in instances:
                # Some instances may be empty in the database
                if (i.points):
                    total_data_points += len(i.points)

        # Finished handling the curve
        print("Fetched {}, with {} instances and {} data points, in {:.2f} seconds".format(
            curve_name, total_instances, total_data_points, time.time() - read_start_time))

# For un-tagged instances, simply take out the tags parts, allowing more instances to be read per call.
