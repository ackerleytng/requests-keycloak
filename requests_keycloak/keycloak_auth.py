"""
requests_keycloak.keycloak_auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a KeycloakAuth authentication handlers

Much of this was inspired by HTTPDigestAuth from requests.auth
"""

import os
import threading

from requests.auth import AuthBase
from requests.cookies import extract_cookies_to_jar

from .keycloak import (
    is_keycloak_login_page,
    parse_post_url,
)


USERNAME_ENVVAR = "AUTOLOGIN_USERNAME"
PASSWORD_ENVVAR = "AUTOLOGIN_PASSWORD"


class KeycloakAuth(AuthBase):
    def __init__(self, username=None, password=None):
        # Allow username and password to be stored as None in KeycloakAuth

        # An alternative would be to getenv in this __init__() and store it,
        #   but that means callers will not be able to dynamically change the
        #   username and password in the environment variables after
        #   KeycloakAuth is initialized

        self.username = username
        self.password = password
        # Keep state in per-thread local storage
        self._thread_local = threading.local()

    def init_per_thread_state(self):
        # Ensure state is initialized just once per-thread
        if not hasattr(self._thread_local, 'init'):
            self._thread_local.init = True
            self._thread_local.pos = None

    def _get_creds(self):
        if self.username is None:
            self.username = os.getenv(USERNAME_ENVVAR)

        if self.password is None:
            self.password = os.getenv(PASSWORD_ENVVAR)

        assert self.username, f"You need to configure {USERNAME_ENVVAR} as an environment variable"
        assert self.password, f"You need to configure {PASSWORD_ENVVAR} as an environment variable"

        return dict(
            username=self.username,
            password=self.password,
        )

    def _check_and_login(
            self,
            response,
            **kwargs
    ):
        if not is_keycloak_login_page(response):
            return response

        post_url = parse_post_url(response.text)
        if not post_url:
            raise Exception("TODO")

        if self._thread_local.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            response.request.body.seek(self._thread_local.pos)

        # Content was consumed earlier when we parsed for post url

        # Release the original connection to allow our new request to reuse the
        #   same one.
        response.close()

        prep = response.request.copy()
        extract_cookies_to_jar(prep._cookies, response.request, response.raw)
        prep.prepare_cookies(prep._cookies)
        prep.prepare_body(data=self._get_creds(), files=None)

        prep.method = "POST"
        prep.url = post_url

        _r = response.connection.send(prep, **kwargs)
        _r.history.append(response)
        _r.request = prep

        # TODO should do a full retry of the first request

        return _r


    def __call__(self, request):
        self.init_per_thread_state()

        try:
            self._thread_local.pos = request.body.tell()
        except AttributeError:
            # In the case of KeycloakAuth being reused and the body of
            # the previous request was a file-like object, pos has the
            # file position of the previous body. Ensure it's set to
            # None.
            self._thread_local.pos = None

        request.register_hook("response", self._check_and_login)

        return request

    def __eq__(self, other):
        return all([
            self.username == getattr(other, "username", None),
            self.password == getattr(other, "password", None)
        ])

    def __ne__(self, other):
        return not self == other
