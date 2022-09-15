from unittest.mock import Mock, patch

import requests

import wapi


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code
        self.content = "Mock content"


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

    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1')

    response = session.data_request('GET', None, '/curves')

    assert response == mock_response


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

