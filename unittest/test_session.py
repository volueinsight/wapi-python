from unittest.mock import Mock, patch, MagicMock

import pytest
import requests

import wapi
import json


class MockResponse:
    def __init__(self, status_code, content="Mock content"):
        self.status_code = status_code
        self.content = content
        

def make_wapi_session():
    return wapi.session.Session(urlbase='https://volueinsight.com',
                                auth_urlbase='https://auth.vs.com',
                                client_id='client1',
                                client_secret='secret1')

# ignore auth
@patch('wapi.session.auth', MagicMock())
@patch('wapi.session.requests')
def test_data_request__get__ok(requests_mock):
    mock_response = MockResponse(200)
    # https://docs.python.org/3/library/unittest.mock-examples.html#mocking-chained-calls
    requests_mock.Session.return_value.request.return_value = mock_response

    session = make_wapi_session()
    response = session.data_request('GET', None, '/curves')

    assert response == mock_response


@patch.object(wapi.session.requests.Session, "request")
def test_data_request__token_expire__ok(mock_request):
    def mock_request_effect(**kwargs):
        if kwargs["method"] == "POST":
            return MockResponse(200, content=json.dumps({"access_token": "a", "token_type": "b", "expires_in": 10}).encode())
        elif kwargs["method"] == "GET":
            return MockResponse(200, "curves")

    mock_request.side_effect = mock_request_effect

    # verify auth getting token at beginning
    session = make_wapi_session()    
    assert session.auth.get_headers(None) == {'Authorization': 'b a'}

    # verify auth refreshing token
    session.auth.valid_until = 0 # simulating token expiring
    response = session.data_request('GET', None, '/curves')

    assert response.status_code == 200
    assert response.content == "curves"
    assert session.auth.get_headers(None) == {'Authorization': 'b a'}


@pytest.mark.parametrize("urlbase,url,longurl_expected", 
    [
        (None, "/token", "https://volueinsight.com/token"), 
        ("http://urlbase", "/token", "http://urlbase/token")
    ])
@patch('wapi.session.auth', MagicMock())
@patch('wapi.session.requests')
def test_send_data_request__long_url__correct(requests_mock, urlbase, url, longurl_expected):
    requests_mock.Session.return_value.request.return_value = MockResponse(200)

    session = make_wapi_session()    
    session.data_request('GET', urlbase=urlbase, url=url)

    call_args = requests_mock.Session.return_value.request.call_args
    assert call_args[1]["url"] == longurl_expected


@pytest.mark.parametrize("data,rawdata,databytes_expected", 
    [
        (None, "rawdata", "rawdata"), 
        (40, None, b"40"), 
        ("basestring", "rawdata", b"basestring")
    ])
@patch('wapi.session.auth', MagicMock())
@patch('wapi.session.requests')
def test_send_data_request__databytes__correct(requests_mock, data, rawdata, databytes_expected):
    requests_mock.Session.return_value.request.return_value = MockResponse(200)

    session =  make_wapi_session()   
    session.data_request('GET', None, None, data=data, rawdata=rawdata)

    call_args = requests_mock.Session.return_value.request.call_args
    assert call_args[1]["data"] == databytes_expected


@pytest.mark.parametrize("failed_status_code", [408, 500, 599])
@patch('wapi.session.auth', MagicMock())
@patch('wapi.session.requests')
def test_send_data_request__retries__correct(requests_mock, failed_status_code):
    requests_mock.Session.return_value.request.return_value = MockResponse(failed_status_code)

    retries_count = 3
    wapi.session.RETRY_DELAY = 0.00001
    session =  make_wapi_session()   
    session.send_data_request("GET", "http://urlbase", "/url", "data", None, "headers", "authval", False, retries_count)

    call_args = requests_mock.Session.return_value.request.call_args
    assert call_args[1] == {"method": "GET", "url": "http://urlbase/url", "data": b"data", "headers": "headers", 
                            "auth": "authval", "stream": False, "timeout": 300}
    assert requests_mock.Session.return_value.request.call_count == retries_count + 1


@patch('wapi.session.auth')
@patch('wapi.session.requests')
def test_data_request__get_auth__first_failed_then_ok(requests_mock, auth_mock):
    mock_response = MockResponse(200)
    requests_mock.Session.return_value.request.return_value = mock_response
    oauth_mock = Mock()
    auth_mock.OAuth.return_value = oauth_mock
    validation_called = []

    def validate_auth():
        validation_called.append(1)
        if len(validation_called) == 1:
            raise requests.exceptions.ConnectionError
        return True

    oauth_mock.validate_auth = validate_auth
    oauth_mock.get_headers.return_value = {'Authorization': 'X Y'}

    wapi.session.RETRY_DELAY = 0.00001
    session = make_wapi_session()
    session.retry_update_auth = True

    response = session.data_request('GET', None, '/curves')

    assert response == mock_response

    assert len(validation_called) == 2
    assert requests_mock.Session.return_value.request.call_count == 1
    call_args = requests_mock.Session.return_value.request.call_args
    assert call_args[1]['method'] == "GET"
    assert call_args[1]['headers'] == {'Authorization': 'X Y'}


@patch('wapi.session.auth')
@patch('wapi.session.requests')
def test_data_request__fail_too_many_times(requests_mock, auth_mock):
    mock_response = MockResponse(200)
    requests_mock.Session.return_value.request.return_value = mock_response
    oauth_mock = Mock()
    auth_mock.OAuth.return_value = oauth_mock
    validation_called = []

    def validate_auth():
        validation_called.append(1)
        raise requests.exceptions.ConnectionError

    oauth_mock.validate_auth = validate_auth
    oauth_mock.get_headers.return_value = {'Authorization': 'X Y'}

    wapi.session.RETRY_DELAY = 0.00001
    session = make_wapi_session()
    session.retry_update_auth = True

    with pytest.raises(requests.exceptions.ConnectionError):
        session.data_request('GET', None, '/curves')

    assert len(validation_called) == 5
    assert requests_mock.Session.return_value.request.call_count == 0

