from datetime import datetime

import pandas as pd
import pytest
import pytz

from wapi.curves import TimeSeriesCurve
from wapi.util import TS, Range

CET = pytz.timezone('CET')


@pytest.fixture
def ts1():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=1, name='This is a Name', frequency='M', time_zone='CET',
              curve_type=TimeSeriesCurve, points=points)


@pytest.fixture
def ts2():
    points = [[0, 120], [2678400000, 210],
              [5097600000, 330], [7776000000, 380]]
    return TS(id=2, name='This is another Name', frequency='M',
              time_zone='CET', curve_type=TimeSeriesCurve, points=points)


@pytest.fixture
def ts3():
    points = [[0, 220], [2678400000, 120],
              [5097600000, 140], [7776000000, 580]]
    return TS(id=3, name='This is a third Name', frequency='M',
              time_zone='CET', curve_type=TimeSeriesCurve, points=points)


def test_ts_to_pandas(ts1):
    pd_series = ts1.to_pandas()
    assert len(pd_series.index) == len(ts1.points)


def test_ts_from_pandas(ts1):
    pd_series = ts1.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts1.name
    assert re_ts.frequency == ts1.frequency
    assert len(re_ts.points) == len(ts1.points)

    for dp1, dp2 in zip(re_ts.points, ts1.points):
        assert dp1 == dp2


def test_ts_sum_ts(ts1, ts2, ts3):
    points = [[0, 420], [2678400000, 420],
              [5097600000, 540], [7776000000, 1080]]
    sum_name = 'Summed Series'
    summed = TS.sum([ts1, ts2, ts3], sum_name)

    assert summed.name == sum_name
    assert summed.frequency == ts1.frequency
    assert len(summed.points) >= len(ts1.points)
    assert len(summed.points) >= len(ts2.points)

    for dp1, dp2 in zip(points, summed.points):
        assert dp1 == dp2


def test_ts_mean_ts(ts1, ts2, ts3):
    points = [[0, 140.0], [2678400000, 140],
              [5097600000, 180], [7776000000, 360]]
    mean_name = 'Mean Series'
    summed = TS.mean([ts1, ts2, ts3], mean_name)

    assert summed.name == mean_name
    assert summed.frequency == ts1.frequency
    assert len(summed.points) >= len(ts1.points)
    assert len(summed.points) >= len(ts2.points)

    for dp1, dp2 in zip(points, summed.points):
        assert dp1 == dp2


def test_ts_median_ts(ts1, ts2, ts3):
    points = [[0, 120.0], [2678400000, 120],
              [5097600000, 140], [7776000000, 380]]
    median_name = 'Median Series'
    summed = TS.median([ts1, ts2, ts3], median_name)

    assert summed.name == median_name
    assert summed.frequency == ts1.frequency
    assert len(summed.points) >= len(ts1.points)
    assert len(summed.points) >= len(ts2.points)

    for dp1, dp2 in zip(points, summed.points):
        assert dp1 == dp2


def test_range_range_dict_non_empty():
    response = {
        'begin': '2009-12-31T23:00:00+00:00',
        'end': '2022-09-29T22:00:00+00:00'
    }
    r = Range.from_dict(response)
    assert '2010-01-01T00:00:00+01:00' == r.begin.isoformat()
    assert '2022-09-30T00:00:00+02:00' == r.end.isoformat()


def test_range_range_dict_empty():
    assert Range.from_dict({}) == Range(None, None)


def test_range_is_finite():
    r = Range(
        CET.localize(datetime(2010, 1, 1, 1)),
        CET.localize(datetime(2022, 9, 30))
    )
    assert r.is_finite()

    r = Range(None, CET.localize(datetime(2022, 9, 30)))
    assert not r.is_finite()

    r = Range(CET.localize(datetime(2022, 9, 30)), None)
    assert not r.is_finite()

    r = Range(None, None)
    assert not r.is_finite()


def test_range_to_pandas():
    r = Range(
        CET.localize(datetime(2010, 1, 1, 1)),
        CET.localize(datetime(2022, 8, 30))
    )
    interval: pd.Interval = r.to_pandas()
    assert interval.left == pd.Timestamp(2010, 1, 1, 1).tz_localize(CET)
    assert interval.right == pd.Timestamp(2022, 8, 30).tz_localize(CET)
