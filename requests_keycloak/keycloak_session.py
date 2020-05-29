import requests

from .keycloak_auth import KeycloakAuth


class KeycloakSession(requests.Session):
    """A special session that, once it sees a keycloak login page, automatically
    logs in for you.

    Requires that redirects are allowed `allow_redirects` defaults to `True`.
    """

    def __init__(self, username=None, password=None):
        super().__init__()

        self.auth = KeycloakAuth(username=username, password=password)
