import pytest

from wapi.util import TS, CurveException, TIME_SERIES, TAGGED, INSTANCES, TAGGED_INSTANCES

from fixtures import ts1, ts2, ts3
from fixtures import ts_tagged, ts_tagged2, ts_tagged3
from fixtures import ts_instance, ts_instance2, ts_instance3
from fixtures import ts_tagged_instance, ts_tagged_instance2, ts_tagged_instance3
from fixtures import ts_empty_points, ts_none_points

from fixtures import ts_tagged_wrong, ts_instance_wrong, ts_tagged_instance_wrong


def test_to_pandas(ts1):
    pd_series = ts1.to_pandas()
    assert len(pd_series.index) == len(ts1.points)


def test_to_pandas_tagged(ts_tagged):
    pd_series = ts_tagged.to_pandas()
    assert len(pd_series.index) == len(ts_tagged.points)


def test_to_pandas_instance(ts_instance):
    pd_series = ts_instance.to_pandas()
    assert len(pd_series.index) == len(ts_instance.points)


def test_to_pandas_tagged_instance(ts_tagged_instance):
    pd_series = ts_tagged_instance.to_pandas()
    assert len(pd_series.index) == len(ts_tagged_instance.points)


def test_from_pandas(ts1):
    pd_series = ts1.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts1.name
    assert re_ts.frequency == ts1.frequency
    assert len(re_ts.points) == len(ts1.points)

    for dp1, dp2 in zip(re_ts.points, ts1.points):
        assert dp1 == dp2


def test_from_pandas_empty(ts_empty_points):
    pd_series = ts_empty_points.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts_empty_points.name
    assert re_ts.frequency == ts_empty_points.frequency
    assert len(re_ts.points) == len(ts_empty_points.points) == 0


def test_from_pandas_none(ts_none_points):
    pd_series = ts_none_points.to_pandas()
    re_ts = TS.from_pandas(pd_series)

    assert re_ts.name == ts_none_points.name
    assert re_ts.frequency == ts_none_points.frequency
    assert len(re_ts.points) == 0


def _agg_validate(result, expected):

    assert result.name == expected.name
    assert result.frequency == expected.frequency
    assert len(result.points) == len(expected.points)

    for dp1, dp2 in zip(result.points, expected.points):
        assert dp1 == dp2


def _sum(ts1, ts2, ts3, data_type=TIME_SERIES):
    points = [[0, 420], [2678400000, 420],
              [5097600000, 540], [7776000000, 1080]]
    expected_ts = TS(name='Summed Series', points=points,
                     frequency=ts1.frequency, curve_type=data_type)
    summed = TS.sum([ts1, ts2, ts3], expected_ts.name, data_type=data_type)
    _agg_validate(summed, expected_ts)
    return summed


def _mean(ts1, ts2, ts3, data_type=TIME_SERIES):
    points = [[0, 140.0], [2678400000, 140],
              [5097600000, 180], [7776000000, 360]]
    expected_ts = TS(name='Mean Series', points=points,
                     frequency=ts1.frequency, curve_type=data_type)
    mean = TS.mean([ts1, ts2, ts3], expected_ts.name, data_type=data_type)

    _agg_validate(mean, expected_ts)
    return mean


def _median(ts1, ts2, ts3, data_type=TIME_SERIES):
    points = [[0, 120.0], [2678400000, 120],
              [5097600000, 140], [7776000000, 380]]
    median_name = 'Median Series'
    expected_ts = TS(name=median_name, points=points,
                     frequency=ts1.frequency, curve_type=data_type)
    median = TS.median([ts1, ts2, ts3], median_name, data_type=data_type)

    _agg_validate(expected_ts, median)
    return median

def test_sum_ts(ts1, ts2, ts3):
    _sum(ts1, ts2, ts3)


def test_sum_ts_tagged(ts_tagged, ts_tagged2, ts_tagged3):
    summed = _sum(ts_tagged, ts_tagged2, ts_tagged3, data_type=TAGGED)
    assert summed.tag == ts_tagged.tag


def test_sum_ts_instance(ts_instance, ts_instance2, ts_instance3):
    summed = _sum(ts_instance, ts_instance2, ts_instance3, data_type=INSTANCES)
    assert summed.issue_date == ts_instance.issue_date


def test_sum_ts_tagged_instance(ts_tagged_instance,
                                ts_tagged_instance2,
                                ts_tagged_instance3):
    summed = _sum(ts_tagged_instance,
                  ts_tagged_instance2,
                  ts_tagged_instance3,
                  data_type=TAGGED_INSTANCES)
    assert summed.tag == ts_tagged_instance.tag
    assert summed.issue_date == ts_tagged_instance.issue_date


def test_mean_ts(ts1, ts2, ts3):
    _mean(ts1, ts2, ts3)


def test_mean_ts_tagged(ts_tagged, ts_tagged2, ts_tagged3):
    mean = _mean(ts_tagged, ts_tagged2, ts_tagged3, data_type=TAGGED)
    assert mean.tag == ts_tagged.tag


def test_mean_ts_instance(ts_instance, ts_instance2, ts_instance3):
    mean = _mean(ts_instance, ts_instance2, ts_instance3,
                 data_type=INSTANCES)
    assert mean.issue_date == ts_instance.issue_date


def test_mean_ts_tagged_instance(ts_tagged_instance,
                                 ts_tagged_instance2,
                                 ts_tagged_instance3):
    mean = _mean(ts_tagged_instance,
                 ts_tagged_instance2,
                 ts_tagged_instance3,
                 data_type=TAGGED_INSTANCES)
    assert mean.tag == ts_tagged_instance.tag
    assert mean.issue_date == ts_tagged_instance.issue_date


def test_median_ts(ts1, ts2, ts3):
    _median(ts1, ts2, ts3)


def test_median_ts_tagged(ts_tagged, ts_tagged2, ts_tagged3):
    median = _median(ts_tagged, ts_tagged2, ts_tagged3, data_type=TAGGED)
    assert median.tag == ts_tagged.tag


def test_median_ts_instance(ts_instance, ts_instance2, ts_instance3):
    median = _median(ts_instance, ts_instance2, ts_instance3,
                     data_type=INSTANCES)
    assert median.issue_date == ts_instance.issue_date


def test_median_ts_tagged_instance(ts_tagged_instance,
                                   ts_tagged_instance2,
                                   ts_tagged_instance3):
    median = _median(ts_tagged_instance,
                     ts_tagged_instance2,
                     ts_tagged_instance3,
                     data_type=TAGGED_INSTANCES)
    assert median.tag == ts_tagged_instance.tag
    assert median.issue_date == ts_tagged_instance.issue_date


def test_tag_validation(ts_tagged_wrong, ts_tagged2, ts_tagged3):
    with pytest.raises(CurveException):
        _sum(ts_tagged_wrong, ts_tagged2, ts_tagged3, data_type=TAGGED)


def test_instances_validation(ts_instance_wrong, ts_instance2, ts_instance3):
    with pytest.raises(CurveException):
        _mean(ts_instance_wrong, ts_instance2, ts_instance3, data_type=INSTANCES)

def test_tag_and_instance_validation(ts_tagged_instance_wrong,
                                     ts_tagged_instance2,
                                     ts_tagged_instance3):
    with pytest.raises(CurveException):
        _median(ts_tagged_instance_wrong,
                ts_tagged_instance2,
                ts_tagged_instance3,
                data_type=TAGGED_INSTANCES)
