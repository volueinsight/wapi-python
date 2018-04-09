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


def test_to_pandas(ts1):
    pd_series = ts1.to_pandas()
    assert len(pd_series.index) == len(ts1.points)


def test_from_pandas(ts1):
    pd_series = ts1.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts1.name
    assert re_ts.frequency == ts1.frequency
    assert len(re_ts.points) == len(ts1.points)

    for dp1, dp2 in zip(re_ts.points, ts1.points):
        assert dp1 == dp2


def test_sum_ts(ts1, ts2):
    points = [[0, 200], [2678400000, 300],
              [5097600000, 400], [7776000000, 500]]
    sum_name = 'Summed Series'
    summed = TS.sum([ts1, ts2], sum_name)

    assert summed.name == sum_name
    assert summed.frequency == ts1.frequency
    assert len(summed.points) >= len(ts1.points)
    assert len(summed.points) >= len(ts2.points)
    print(summed.points)

    for dp1, dp2 in zip(points, summed.points):
        assert dp1 == dp2
