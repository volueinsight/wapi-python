import pytest
from wapi.util import TS
from wapi.curves import TimeSeriesCurve, TaggedCurve, InstanceCurve, TaggedInstanceCurve

from datetime import datetime, timedelta

_issue_date = datetime.now().isoformat()
_test_tag = 'TESTTAG'
_error_date = (datetime.now() - timedelta(days=1)).isoformat()
_error_tag = 'WRONG TAG'

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
def ts_empty_points():
    return TS(id=4, name='Fourth timeseries', frequency='M',
              time_zone='CET', curve_type=TimeSeriesCurve, points=[])


@pytest.fixture
def ts_none_points():
    return TS(id=5, name='Fifth timeseries', frequency='M',
              time_zone='CET', curve_type=TimeSeriesCurve)


@pytest.fixture
def ts_tagged():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=6, name='Tagged TS', frequency='M', tag=_test_tag,
              time_zone='CET', curve_type=TaggedCurve,
              points=points)


@pytest.fixture
def ts_tagged2():
    points = [[0, 120], [2678400000, 210],
              [5097600000, 330], [7776000000, 380]]
    return TS(id=7, name='Tagged TS 2', frequency='M', tag=_test_tag,
              time_zone='CET', curve_type=TaggedCurve, points=points)


@pytest.fixture
def ts_tagged3():
    points = [[0, 220], [2678400000, 120],
              [5097600000, 140], [7776000000, 580]]
    return TS(id=8, name='Tagged TS 3', frequency='M', tag=_test_tag,
              time_zone='CET', curve_type=TaggedCurve, points=points)


@pytest.fixture
def ts_instance():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=9, name='Instance TS', frequency='M', issue_date=_issue_date,
              time_zone='CET', curve_type=InstanceCurve, points=points)


@pytest.fixture
def ts_instance2():
    points = [[0, 120], [2678400000, 210],
              [5097600000, 330], [7776000000, 380]]
    return TS(id=10, name='Instance TS 2', frequency='M', issue_date=_issue_date,
              time_zone='CET', curve_type=InstanceCurve, points=points)


@pytest.fixture
def ts_instance3():
    points = [[0, 220], [2678400000, 120],
              [5097600000, 140], [7776000000, 580]]
    return TS(id=11, name='Instance TS 3', frequency='M', issue_date=_issue_date,
              time_zone='CET', curve_type=InstanceCurve, points=points)


@pytest.fixture
def ts_tagged_instance():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=12, name='Tagged Instance TS', frequency='M', tag=_test_tag,
              issue_date=_issue_date, time_zone='CET',
              curve_type=TaggedInstanceCurve, points=points)


@pytest.fixture
def ts_tagged_instance2():
    points = [[0, 120], [2678400000, 210],
              [5097600000, 330], [7776000000, 380]]
    return TS(id=13, name='Tagged Instance TS 2', frequency='M', tag=_test_tag,
              issue_date=_issue_date, time_zone='CET',
              curve_type=TaggedInstanceCurve, points=points)


@pytest.fixture
def ts_tagged_instance3():
    points = [[0, 220], [2678400000, 120],
              [5097600000, 140], [7776000000, 580]]
    return TS(id=14, name='Tagged Instance TS 3', frequency='M', tag=_test_tag,
              issue_date=_issue_date, time_zone='CET',
              curve_type=TaggedInstanceCurve, points=points)


@pytest.fixture
def ts_tagged_wrong():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=7, name='Tagged TS', frequency='M', tag=_error_tag,
              time_zone='CET', curve_type=TaggedCurve,
              points=points)


@pytest.fixture
def ts_instance_wrong():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=9, name='Instance TS', frequency='M', issue_date=_error_date,
              time_zone='CET', curve_type=InstanceCurve, points=points)


@pytest.fixture
def ts_tagged_instance_wrong():
    points = [[0, 80], [2678400000, 90],
              [5097600000, 70], [7776000000, 120]]
    return TS(id=12, name='Tagged Instance TS', frequency='M', tag=_error_tag,
              issue_date=_error_date, time_zone='CET',
              curve_type=TaggedInstanceCurve, points=points)

