from unittest.mock import Mock, patch

import pytest
import requests

import wapi
import json


class MockResponse:
    def __init__(self, status_code, content="Mock content"):
        self.status_code = status_code
        self.content = content


@patch('wapi.session.auth')
@patch('wapi.session.requests')
def test_data_request__get_auth__ok(requests_mock, auth_mock):
    mock_response = MockResponse(200)
    req_session_mock = Mock()
    req_session_mock.request.return_value = mock_response
    requests_mock.Session.return_value = req_session_mock
    oauth_mock = Mock()
    auth_mock.OAuth.return_value = oauth_mock
    oauth_mock.get_headers.return_value = {'Authorization': 'X Y'}

    wapi.session.RETRY_DELAY = 0.00001
    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1')

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
    wapi.session.RETRY_DELAY = 0.00001

    # verify auth getting token at beginning
    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1')

    assert session.auth.get_headers(None) == {'Authorization': 'b a'}

    # verify auth refreshing token
    session.auth.valid_until = 0 # simulating token expiring
    response = session.data_request('GET', None, '/curves')

    assert response.status_code == 200
    assert response.content == "curves"
    assert session.auth.get_headers(None) == {'Authorization': 'b a'}


@patch('wapi.session.auth')
@patch('wapi.session.requests')
def test_data_request__get_auth__first_failed_then_ok(requests_mock, auth_mock):
    mock_response = MockResponse(200)
    req_session_mock = Mock()
    req_session_mock.request.return_value = mock_response
    requests_mock.Session.return_value = req_session_mock
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
    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1',
                                   retry_update_auth=True)

    response = session.data_request('GET', None, '/curves')

    assert response == mock_response

    assert len(validation_called) == 2
    assert req_session_mock.request.call_count == 1
    call_args = req_session_mock.request.call_args
    assert call_args[1]['method'] == "GET"
    assert call_args[1]['headers'] == {'Authorization': 'X Y'}


@patch('wapi.session.auth')
@patch('wapi.session.requests')
def test_data_request__fail_too_many_times(requests_mock, auth_mock):
    mock_response = MockResponse(200)
    req_session_mock = Mock()
    req_session_mock.request.return_value = mock_response
    requests_mock.Session.return_value = req_session_mock
    oauth_mock = Mock()
    auth_mock.OAuth.return_value = oauth_mock
    validation_called = []

    def validate_auth():
        validation_called.append(1)
        raise requests.exceptions.ConnectionError

    oauth_mock.validate_auth = validate_auth
    oauth_mock.get_headers.return_value = {'Authorization': 'X Y'}

    wapi.session.RETRY_DELAY = 0.00001
    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1',
                                   retry_update_auth=True)

    with pytest.raises(requests.exceptions.ConnectionError):
        session.data_request('GET', None, '/curves')

    assert len(validation_called) == 5
    assert req_session_mock.request.call_count == 0

