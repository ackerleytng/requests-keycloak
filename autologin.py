import os
import re
import html
from urllib.parse import urlparse, parse_qs

import requests


USERNAME_ENVVAR = "AUTOLOGIN_USERNAME"
PASSWORD_ENVVAR = "AUTOLOGIN_PASSWORD"

KEYCLOAK_TO_CHECK = dict(
    query_params={"state", "client_id", "response_type", "scope", "redirect_uri"},
    response_type=["code"],
)


def _is_keycloak_login_page(response):
    """Given a requests.Response, returns True if it (heuristically) is a keycloak
    login page, or False otherwise
    """

    u = urlparse(response.url)
    qs = parse_qs(u.query)

    parsed = dict(
        query_params=set(qs),
        response_type=qs.get("response_type"),
    )

    return (
        parsed == KEYCLOAK_TO_CHECK and
        u.path.startswith("/auth/realms/") and
        u.path.endswith("/protocol/openid-connect/auth")
    )


def _parse_post_url(page):
    """Parses given html page for post url and returns the html-unescaped version
    of it.

    Returns None of the page doesn't contain the post url we're looking for
    """
    for l in page.split("\n"):
        if "kc-form-login" in l:
            m = re.search(r' action="(.*?)" ', l)
            if m:
                return html.unescape(m.group(1))


class AutoLoginSession(requests.Session):
    """A special session that, once it sees a keycloak login page, automatically
    logs in for you.

    Requires that redirects are allowed `allow_redirects` defaults to `True`.
    """

    def request(
            self, method, url,
            params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None
    ):
        assert allow_redirects, "AutoLoginSessions can only work if redirects are permitted"

        r = super().request(
            method, url,
            params=params, data=data, headers=headers, cookies=cookies, files=files,
            auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies,
            hooks=hooks, stream=stream, verify=verify, cert=cert, json=json
        )

        # Hint: If you need to debug, it would be useful to print out the
        #   intermediate page here with
        # print(r.text)

        if _is_keycloak_login_page(r):
            username = os.getenv(USERNAME_ENVVAR)
            password = os.getenv(PASSWORD_ENVVAR)

            assert username, f"You need to configure {USERNAME_ENVVAR} as an environment variable"
            assert password, f"You need to configure {PASSWORD_ENVVAR} as an environment variable"

            post_url = _parse_post_url(r.text)
            if not post_url:
                raise Exception("TODO")

            data = dict(
                username=username,
                password=password,
            )

            # Use super()'s post to avoid going through this instance's
            #   request() again with this second call

            # If the login works, there should be to second call anyway If the
            #   login doesn't work (e.g. username/password wrong or whatever),
            #   we will return whatever we get redirected to. This is expected
            #   behaviour.

            # Instead of handling all possible errors, we let the user of the
            #   library find out what the problem is and address it

            # Another possible outcome is that after logging in, keycloak
            #   requires the user to change his/her password. In that case, the
            #   user should change the password manually and re-run his/her
            #   script
            r = super().post(post_url, data=data, verify=verify)

        return r
