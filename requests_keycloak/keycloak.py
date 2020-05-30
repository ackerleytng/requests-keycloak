import re
import html
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests


KEYCLOAK_TO_CHECK = dict(
    query_params={"state", "client_id", "response_type", "scope", "redirect_uri"},
    response_type=["code"],
)


def is_keycloak_login_url(url: str) -> bool:
    """Given a url, returns True if it (heuristically) is keycloak's login page, or
    False otherwise
    """

    u = urlparse(url)
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


def parse_post_url(page: str) -> Optional[str]:
    """Parses given html page (the keycloak login page) for the submit url of the
    username/password form and returns the html-unescaped version of it.

    Returns None of the page doesn't contain the post url we're looking for.
    """
    for l in page.split("\n"):
        if "kc-form-login" in l:
            m = re.search(r' action="(.*?)" ', l)
            if m:
                return html.unescape(m.group(1))
