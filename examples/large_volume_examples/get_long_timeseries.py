"""
This example shows an approach to downloading long time series
in a safe but efficient way.  Typically used for getting long normals.
"""

import wapi
from datetime import timedelta
from dateutil.parser import parse
from zoneinfo import ZoneInfo
import time

############################################
# Insert the path to your config file here!
my_config_file = 'path/to/your/config.ini'
############################################

# Create a session to Connect to Wattsight Database
session = wapi.Session(config_file=my_config_file)

# As an example, we read the wind production normals
# for some regions.  These are long series, we cannot
# read the whole range at once.

CET = ZoneInfo("CET")

# Just grab some possible start/end dates if we cannot
# find them from the curve metadata.
# At some point we will annotate the curve objects with
# the actually available start/end date
default_start_date = parse('2010-01-01T00:00+01:00').astimezone(CET)
default_end_date = parse('2030-01-01T00:00+01:00').astimezone(CET)

# There is a max number of datapoints per request, which
# is adjusted to keep things robust.  This is usually OK,
# reduce the number if you get errors.
max_datapoints = 250_000.0
datapoints_per_day = 24 * 4  # min15 frequency here
max_days = int(max_datapoints / datapoints_per_day)

regions = ['fr','es','de']

for r in regions:
    # curve name to read, based on the region
    curve_name = 'pro ' + r + ' wnd mwh/h cet min15 n'
    # get the curve
    curve = session.get_curve(name=curve_name)
    if curve.accessRange['begin'] is None:
        start_date = default_start_date
    else:
        start_date = parse(curve.accessRange['begin']).astimezone(CET)
    if curve.accessRange['end'] is None:
        end_date = default_end_date
    else:
        end_date = parse(curve.accessRange['end']).astimezone(CET)

    read_start_time = time.time()

    # Time to loop along the time axis
    ts = None
    end_frag = start_date
    while end_frag < end_date:
        # Find start/end dates for reading this fragment
        start_frag = end_frag
        end_frag = end_frag + timedelta(days=max_days)
        if end_frag > end_date:
            end_frag = end_date

        # Fetch fragment data from WAPI
        frag = curve.get_data(data_from=start_frag, data_to=end_frag)

        # Remove empty elements at start/end of time series
        i = 0
        l = len(frag.points)
        while i < l and frag.points[i][1] is None:
            i += 1
        j = l
        while j > i and frag.points[j-1][1] is None:
            j -= 1
        frag.points = frag.points[i:j]

        if ts is None:
            ts = frag
        else:
            ts.points.extend(frag.points)

        # If we are at the end of the available data, optimize a bit
        if len(ts.points) > 0 and len(frag.points) == 0:
            break

    # Now do whatever processing you need on the full series
    print("Fetched {}, with {} data points, in {:.2f} seconds".format(
        curve_name, len(ts.points), time.time() - read_start_time))

# For a tagged series, simply loop over the list returned by 'curve.get_tags()'
# in the middle of things, fetching the full range of data for each tag as above.
