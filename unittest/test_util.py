import pytest

from wapi.curves import TimeSeriesCurve
from wapi.util import TS


@pytest.fixture
def ts():
    points = [[1000, 80], [267480000, 90], [10364400000, 70]]
    return TS(id=1, name='This is a Name', frequency='M', time_zone='CET',
              curve_type=TimeSeriesCurve, points=points)


@pytest.fixture
def ts2():
    points = [[1000, 0], [509400000, 200], [1036440000, 70]]
    return TS(id=2, name='This is another Name', frequency='M', time_zone='CET',
              curve_type=TimeSeriesCurve, points=points)


def test_to_pandas(ts):
    pd_series = ts.to_pandas()

    assert len(pd_series.index) == len(ts.points)


def test_from_pandas(ts):
    pd_series = ts.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts.name
    assert re_ts.frequency == ts.frequency
    assert len(re_ts.points) == len(ts.points)
    for dp1, dp2 in zip(ts.points, re_ts.points):
        assert dp1 == dp2


def test_sum_ts(ts, ts2):
    # print(ts)
    sum_name = 'Summed Series'
    summed = TS.sum([ts, ts2], sum_name)

    assert summed.name == ts.name
    assert summed.frequency == ts.frequency
    assert len(summed.points) >= len(ts.points)
    assert len(summed.points) >= len(ts2.points)


test_sum_ts(ts, ts2)
