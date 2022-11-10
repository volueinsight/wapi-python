import pytest

from wapi.curves import TimeSeriesCurve
from wapi.util import TS


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

@pytest.fixture
def ts4():
    points = [
        [2153343600000, 10],
        [2153426400000, 20],
        [2153512800000, 30]
    ]
    return TS(id=4, name='Test 2038 issue', frequency='D',
              time_zone='CET', curve_type=TimeSeriesCurve, points=points)

def test_to_pandas_2038(ts4):
    pd_series = ts4.to_pandas()
    assert len(pd_series.index) == len(ts4.points)

def test_to_pandas(ts1):
    pd_series = ts1.to_pandas()
    assert len(pd_series.index) == len(ts1.points)


def test_from_pandas(ts1):
    pd_series = ts1.to_pandas()
    print("pd_series", pd_series)
    re_ts = TS.from_pandas(pd_series)
    print("re_ts", re_ts)

    assert re_ts.name == ts1.name
    assert re_ts.frequency == ts1.frequency
    assert len(re_ts.points) == len(ts1.points)

    for dp1, dp2 in zip(re_ts.points, ts1.points):
        assert dp1 == dp2


def test_sum_ts(ts1, ts2, ts3):
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


def test_mean_ts(ts1, ts2, ts3):
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


def test_median_ts(ts1, ts2, ts3):
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
