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

    validation_called = 0
    def validate_auth():
        validation_called = validation_called + 1
        if validation_called == 1:
            raise requests.exceptions.ConnectionError
        return True

    # auth_mock.validate_auth = validate_auth
    auth_mock.validate_auth.return_value = 123

    # auth_mock.validate_auth.side_effect = [requests.exceptions.ConnectionError, requests.exceptions.ConnectionError]
    oauth_mock.get_headers.return_value = {'Authorization': 'X Y'}

    session = wapi.session.Session(urlbase='https://volueinsight.com',
                                   auth_urlbase='https://auth.vs.com',
                                   client_id='client1',
                                   client_secret='secret1')

    response = session.data_request('GET', None, '/curves')

    assert response == mock_response

    assert auth_mock.validate_auth.call_count == 2

