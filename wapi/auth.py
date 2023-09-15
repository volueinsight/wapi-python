#
# Authentication support
#

import imp
import json
import time
import threading

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class AuthFailedException(Exception):
    pass


class OAuth:
    """
    Authentication based on OAuth client ID.
    This is the main authentication mechanism for customer access to the data center.
    """

    def __init__(self, session, client_id, client_secret, auth_urlbase):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_urlbase = auth_urlbase
        self.token = None
        self.token_type = None
        self.valid_until = None
        self.session = session
        self._authenticate()

    def validate_auth(self):
        """Check valid_until and fetch new token if needed"""
        # To avoid sending duplicated authentication requests in other threads
        with threading.Lock():
            if (not self.valid_until) or time.time() > self.valid_until:
                self._authenticate()

    def _authenticate(self):
        # Wipe out any old values before (re-)login
        self.token = None
        self.token_type = None
        self.valid_until = None
        now = time.time()
        url = urljoin(self.auth_urlbase, '/oauth2/token')
        auth = (self.client_id, self.client_secret)
        data = {'grant_type': 'client_credentials'}
        response = self.session.send_data_request('POST', self.auth_urlbase, url, rawdata=data, authval=auth)
        if response.status_code != 200:
            raise AuthFailedException('Authentication failed: {}'.format(response.content))
        # Parse token
        rsp = json.loads(response.content.decode())
        self.token = rsp['access_token']
        self.token_type = rsp['token_type']
        self.valid_until = now + int(rsp['expires_in'] * 0.95)

    def get_headers(self, data):
        """The web-token auth header is simple"""
        if self.token is not None and self.token_type is not None:
            return {'Authorization': '{} {}'.format(self.token_type, self.token)}
        return {}
