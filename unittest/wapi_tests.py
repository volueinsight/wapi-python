import json
import os

import pytest
import requests_mock
import time

import wapi

prefix = 'rtsp://test.host/api'
authprefix = 'rtsp://auth.host/oauth2'


#
# Test session and authentication setup
#
def test_build_sessions():
    s = wapi.Session()
    assert s.urlbase == 'https://api.wattsight.com'
    assert s.auth is None
    s = wapi.Session(urlbase ='test_data')
    assert s.urlbase == 'test_data'


def test_configure_by_file():
    config_file = os.path.join(os.path.dirname(__file__), 'testconfig_oauth.ini')
    s = wapi.Session(urlbase='rtsp://test.host')
    #
    mock = requests_mock.Adapter()
    # urllib does things based on protocol, so (ab)use one which is reasonably
    # http-like instead of inventing our own.
    s._session.mount('rtsp', mock)
    client_token = json.dumps({'token_type': 'Bearer', 'access_token': 'secrettoken',
                               'expires_in': 1000})
    mock.register_uri('POST', authprefix + '/token', text=client_token)
    #
    s.read_config_file(config_file)
    assert s.urlbase == 'rtsp://test.host'
    assert isinstance(s.auth, wapi.auth.OAuth)
    assert s.auth.client_id == 'clientid'
    assert s.auth.client_secret == 'verysecret'
    assert s.auth.auth_urlbase == 'rtsp://auth.host'
    assert s.auth.token_type == 'Bearer'
    assert s.auth.token == 'secrettoken'
    lifetime = s.auth.valid_until - time.time()
    assert lifetime > 900
    assert lifetime < 1010


def test_configure_by_param():
    s = wapi.Session(urlbase='rtsp://test.host')
    #
    mock = requests_mock.Adapter()
    # urllib does things based on protocol, so (ab)use one which is reasonably
    # http-like instead of inventing our own.
    s._session.mount('rtsp', mock)
    client_token = json.dumps({'token_type': 'Bearer', 'access_token': 'secrettoken',
                               'expires_in': 1000})
    mock.register_uri('POST', authprefix + '/token', text=client_token)
    #
    s.configure(client_id='clientid', client_secret='verysecret', auth_urlbase='rtsp://auth.host')
    assert s.urlbase == 'rtsp://test.host'
    assert isinstance(s.auth, wapi.auth.OAuth)
    assert s.auth.client_id == 'clientid'
    assert s.auth.client_secret == 'verysecret'
    assert s.auth.auth_urlbase == 'rtsp://auth.host'
    assert s.auth.token_type == 'Bearer'
    assert s.auth.token == 'secrettoken'
    lifetime = s.auth.valid_until - time.time()
    assert lifetime > 900
    assert lifetime < 1010


def test_reconfigure_session():
    config_file = os.path.join(os.path.dirname(__file__), 'testconfig_oauth.ini')
    s = wapi.Session(urlbase='test_data')
    #
    mock = requests_mock.Adapter()
    # urllib does things based on protocol, so (ab)use one which is reasonably
    # http-like instead of inventing our own.
    s._session.mount('rtsp', mock)
    client_token = json.dumps({'token_type': 'Bearer', 'access_token': 'secrettoken',
                               'expires_in': 1000})
    mock.register_uri('POST', authprefix + '/token', text=client_token)
    #
    s.read_config_file(config_file)
    assert s.urlbase == 'rtsp://test.host'
    with pytest.raises(wapi.session.ConfigException) as exinfo:
        s.configure('clientid', 'clientsecret')
    assert 'already done' in str(exinfo.value)

#
# Fixtures to set up the session for the rest of the tests
# Returns both a session and a request mock linked into the session.
#

@pytest.fixture
def session():
    config_file = os.path.join(os.path.dirname(__file__), 'testconfig_oauth.ini')
    s = wapi.Session()
    mock = requests_mock.Adapter()
    s._session.mount('rtsp', mock)
    client_token = json.dumps({'token_type': 'Bearer', 'access_token': 'secrettoken',
                               'expires_in': 1000})
    mock.register_uri('POST', authprefix + '/token', text=client_token)
    s.read_config_file(config_file)
    return s, mock

#
# Test the various authorization headers
#

def test_login_header(session):
    s,m = session
    m.register_uri('GET', prefix + '/units', text='{"res": "ok"}',
                   request_headers={'Authorization': '{} {}'.format(s.auth.token_type,
                                                                    s.auth.token)})
    r = s.get_attribute('units')
    assert r['res'] == 'ok'


#
# Test curves
#

def test_search(session):
    s,m = session
    metadata = [{'id': 5, 'name': 'testcurve5',
                'frequency': 'H', 'time_zone': 'CET',
                'curve_type': 'TIME_SERIES'},
                {'id': 6, 'name': 'testcurve6',
                'frequency': 'D', 'time_zone': 'CET',
                'curve_type': 'INSTANCES'}]
    m.register_uri('GET', prefix + '/curves?name=testcurve5&name=testcurve6', text=json.dumps(metadata))
    c = s.search(name=['testcurve5', 'testcurve6'])
    assert len(c) == 2
    assert isinstance(c[0], wapi.curves.TimeSeriesCurve)
    assert isinstance(c[1], wapi.curves.InstanceCurve)

@pytest.fixture
def ts_curve(session):
    s,m = session
    metadata = {'id': 5, 'name': 'testcurve5',
                'frequency': 'H', 'time_zone': 'CET',
                'curve_type': 'TIME_SERIES'}
    m.register_uri('GET', prefix + '/curves/get?name=testcurve5', text=json.dumps(metadata))
    c = s.get_curve(name='testcurve5')
    return c,s,m

def test_time_series(ts_curve):
    c,s,m = ts_curve
    assert isinstance(c, wapi.curves.TimeSeriesCurve)
    assert c.id == 5
    assert c.name == 'testcurve5'
    assert c.frequency == 'H'
    assert c.time_zone == 'CET'

def test_ts_data(ts_curve):
    c,s,m = ts_curve
    datapoints = {'id': 5, 'frequency': 'H', 'points': [[140000000000, 10.0]]}
    m.register_uri('GET', prefix + '/series/5?from=1&to=2', text=json.dumps(datapoints))
    d = c.get_data(data_from=1, data_to=2)
    assert isinstance(d, wapi.util.TS)
    assert d.frequency == 'H'


@pytest.fixture
def tagged_curve(session):
    s,m = session
    metadata = {'id': 9, 'name': 'testcurve9',
                'frequency': 'H', 'time_zone': 'CET',
                'curve_type': 'TAGGED'}
    m.register_uri('GET', prefix + '/curves/get?name=testcurve9', text=json.dumps(metadata))
    c = s.get_curve(name='testcurve9')
    return c,s,m

def test_tagged(tagged_curve):
    c,s,m = tagged_curve
    assert isinstance(c, wapi.curves.TaggedCurve)
    assert c.id == 9
    assert c.name == 'testcurve9'
    assert c.frequency == 'H'
    assert c.time_zone == 'CET'

def test_tagged_tags(tagged_curve):
    c,s,m = tagged_curve
    tags = {'test': 'ok'}
    m.register_uri('GET', prefix + '/series/tagged/9/tags', text=json.dumps(tags))
    res = c.get_tags()
    assert res['test'] == 'ok'

def test_tagged_data(tagged_curve):
    c,s,m = tagged_curve
    datapoints = [{'id': 9, 'tag': 'tag1', 'frequency': 'H', 'points': [[140000000000, 10.0]]}]
    m.register_uri('GET', prefix + '/series/tagged/9?tag=tag1', text=json.dumps(datapoints))
    d = c.get_data(tag='tag1')
    assert isinstance(d, wapi.util.TS)
    assert d.frequency == 'H'
    assert d.tag == 'tag1'


@pytest.fixture
def inst_curve(session):
    s,m = session
    metadata = {'id': 7, 'name': 'testcurve7',
                'frequency': 'D', 'time_zone': 'CET',
                'curve_type': 'INSTANCES'}
    m.register_uri('GET', prefix + '/curves/get?name=testcurve7', text=json.dumps(metadata))
    c = s.get_curve(name='testcurve7')
    return c,s,m

def test_inst_curve(inst_curve):
    c,s,m = inst_curve
    assert isinstance(c, wapi.curves.InstanceCurve)
    assert c.id == 7
    assert c.name == 'testcurve7'
    assert c.frequency == 'D'
    assert c.time_zone == 'CET'

def test_inst_search(inst_curve):
    c,s,m = inst_curve
    search_data = [
        {'frequency': 'H', 'points': [[140000000000, 10.0]],
         'name': 'inst_name', 'id': 10,
         'issue_date': '46'},
        {'frequency': 'H', 'points': [[140000000000, 10.0]],
         'name': 'inst_name', 'id': 10,
         'issue_date': '50'}]
    m.register_uri('GET', prefix + '/instances/7?issue_date=46&issue_date=50',
                   text=json.dumps(search_data))
    res = c.search_instances(issue_dates=['46', '50'])
    assert len(res) == 2

def test_inst_get_instance(inst_curve):
    c,s,m = inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 7,
            'issue_date': '2016-01-01T00:00Z'}
    m.register_uri('GET',
                   prefix + '/instances/7/get?issue_date=2016-01-01T00:00Z&with_data=true',
                   text=json.dumps(inst))
    res = c.get_instance(issue_date='2016-01-01T00:00Z')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'

def test_inst_get_latest(inst_curve):
    c,s,m = inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 7,
            'issue_date': '2016-01-01T00:00Z'}
    m.register_uri('GET', prefix + '/instances/7/latest?with_data=false&issue_date=56',
                   text=json.dumps(inst))
    res = c.get_latest(issue_dates=56, with_data=False)
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'

def test_inst_get_relative(inst_curve):
    c,s,m = inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 7}
    m.register_uri('GET', prefix + '/instances/7/relative?data_offset=PT1H&issue_date_from=2016-01-01' +
                                   '&issue_date_to=2016-02-01&data_max_length=PT1H',
                   text=json.dumps(inst))
    res = c.get_relative(data_offset='PT1H', data_max_length='PT1H', issue_date_from='2016-01-01',
                         issue_date_to='2016-02-01')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'

def test_inst_get_absolute(inst_curve):
    c,s,m = inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 7}
    m.register_uri('GET', prefix + '/instances/7/absolute?data_date=2016-01-01T12:00&issue_frequency=H' +
                                   '&issue_date_from=2016-01-01&issue_date_to=2016-02-01',
                   text=json.dumps(inst))
    res = c.get_absolute(data_date='2016-01-01T12:00', issue_frequency='H', issue_date_from='2016-01-01',
                         issue_date_to='2016-02-01')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'


@pytest.fixture
def tagged_inst_curve(session):
    s,m = session
    metadata = {'id': 10, 'name': 'testcurve10',
                'frequency': 'D', 'time_zone': 'CET',
                'curve_type': 'TAGGED_INSTANCES'}
    m.register_uri('GET', prefix + '/curves/get?name=testcurve10', text=json.dumps(metadata))
    c = s.get_curve(name='testcurve10')
    return c,s,m

def test_tagged_inst_curve(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    assert isinstance(c, wapi.curves.TaggedInstanceCurve)
    assert c.id == 10
    assert c.name == 'testcurve10'
    assert c.frequency == 'D'
    assert c.time_zone == 'CET'

def test_tagged_inst_tags(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    tags = {'test': 'ok'}
    m.register_uri('GET', prefix + '/instances/tagged/10/tags', text=json.dumps(tags))
    res = c.get_tags()
    assert res['test'] == 'ok'

def test_tagged_inst_search(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    search_data = [
        {'frequency': 'H', 'points': [[140000000000, 10.0]],
         'name': 'inst_name', 'id': 10, 'tag': 'tag1',
         'issue_date': '46'},
        {'frequency': 'H', 'points': [[140000000000, 10.0]],
         'name': 'inst_name', 'id': 10, 'tag': 'tag1',
         'issue_date': '50'}]
    m.register_uri('GET', prefix + '/instances/tagged/10?tag=tag1&issue_date=46&issue_date=50',
                   text=json.dumps(search_data))
    res = c.search_instances(tags='tag1', issue_dates=['46', '50'])
    assert len(res) == 2

def test_tagged_inst_get_instance(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    inst = [{'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 10, 'tag': 'tag1',
            'issue_date': '2016-01-01T00:00Z'}]
    m.register_uri('GET',
                   prefix + '/instances/tagged/10/get?tag=tag1&issue_date=2016-01-01T00:00Z&with_data=true',
                   text=json.dumps(inst))
    res = c.get_instance(tag='tag1', issue_date='2016-01-01T00:00Z')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'
    assert res.tag == 'tag1'

def test_tagged_inst_get_latest(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 10, 'tag': 'tag1',
            'issue_date': '2016-01-01T00:00Z'}
    m.register_uri('GET', prefix + '/instances/tagged/10/latest?with_data=false&issue_date=56',
                   text=json.dumps(inst))
    res = c.get_latest(issue_dates=56, with_data=False)
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'
    assert res.tag == 'tag1'

def test_tagged_inst_get_relative(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 10, 'tag': 'tag1'}
    m.register_uri('GET', prefix + '/instances/tagged/10/relative?data_offset=PT1H&issue_date_from=2016-01-01' +
                                   '&issue_date_to=2016-02-01&data_max_length=PT1H&tag=tag1',
                   text=json.dumps(inst))
    res = c.get_relative(data_offset='PT1H', data_max_length='PT1H', issue_date_from='2016-01-01',
                         issue_date_to='2016-02-01', tag='tag1')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'
    assert res.tag == 'tag1'

def test_tagged_inst_get_absolute(tagged_inst_curve):
    c,s,m = tagged_inst_curve
    inst = {'frequency': 'H', 'points': [[140000000000, 10.0]],
            'name': 'inst_name', 'id': 10, 'tag': 'tag1'}
    m.register_uri('GET', prefix + '/instances/tagged/10/absolute?data_date=2016-01-01T12:00&issue_frequency=H' +
                                   '&tag=tag1&issue_date_from=2016-01-01&issue_date_to=2016-02-01',
                   text=json.dumps(inst))
    res = c.get_absolute(data_date='2016-01-01T12:00', issue_frequency='H', issue_date_from='2016-01-01',
                         issue_date_to='2016-02-01', tag='tag1')
    assert isinstance(res, wapi.util.TS)
    assert res.frequency == 'H'
    assert res.name == 'inst_name'
    assert res.tag == 'tag1'


#
# Test events
#

def test_events(session, ts_curve, inst_curve):
    s, m = session
    c1 = ts_curve[0]
    c2 = inst_curve[0]
    sse_data = []
    ids = [5, 7, 7, 7, 5, 5, 7]
    for n, id in enumerate(ids):
        d = {'id': id, 'created': '2016-10-01T00:01:02.345+01:00', 'operation': 'modify',
             'range': [None, None]}
        sse_data.append('id: {}\nevent: curve_event\ndata: {}\n\n'.format(n, json.dumps(d)))
    m.register_uri('GET', prefix + '/events?id=5&id=7', text=''.join(sse_data))
    with wapi.events.EventListener(s, [c1, c2]) as e:
        for n, id in enumerate(ids):
            event = e.get()
            assert isinstance(event, wapi.events.CurveEvent)
            assert event.id == id
            assert isinstance(event.curve, wapi.curves.BaseCurve)
