# Design decisions

## Design

keycloak-requests was built to wrap around OAuth 2.0's authorization code flow,
specifically with Keycloak as the authorization provider.

In the authorization code flow, unauthenticated requests will be redirected to
keycloak, where the user is expected to authenticate.

After authenticating, the User Agent (the code using requests here) will then
be redirected back to the OAuth client with the authorization code.

Cookies are used to store the user's session with keycloak, and the User-Agent
has to be able to follow redirects.

> `allow_redirects` has to be set to `True` for this library to work

The redirect is the mechanism through which the authorization code flow passes
the authorization code back to the OAuth 2.0 client though the User Agent

### What keycloak-requests does

#### When being redirected to keycloak

When being redirected to a url that looks like a keycloak
authentication page, keycloak-requests will turn the request into a `GET`
regardless of the original request's method.

We do this because the keycloak authentication page only responds to `GET`
requests.

#### When it sees a keycloak authentication page

When it sees a keycloak authentication page, it'll fill in the username and
password and submit it to keycloak.

The submit url is found by scraping and parsing the html, and so this is a
point of concern if the login page's design changes (perhaps due to a Keycloak
upgrade).


## Monkeypatching

keycloak-requests, by design, requires following redirects, and in requests,
redirects are implemented in a tight loop in `resolve_redirects()`. See
[sessions.py](https://github.com/psf/requests/blob/master/requests/sessions.py).

This means as a plugin, we don't have access to influence the redirecting that
happens within that loop.

It may seem like the `__call__` method in an `Auth` class is the right place to
check whether the redirect target is the keycloak authentication page, but that
doesn't work because the `__call__` method is only called before the first
request that `requests` makes, and in this case the first request is probably
not the one that is going to keycloak.

Monkeypatching `rebuild_method` is the relatively safe, because I'm influencing
a method that is rather precisely meant for changing the method in-between
redirects. This means that I'm not overloading a method used for other reasons.

Also, patching is precise: I only override the method when it the requested
destination url is Keycloak's authentication page, so it should not affect any
other functionality.

### Permanence of monkeypatching

In this implementation, the monkeypatch is applied once the `keycloak_auth`
module is imported, and that happens as long as `KeycloakAuth` is used.

I think this is safe because we do want the additional check in
`rebuild_method` as long as the library is active.

### Alternative: Subclassing `Session`

One alternative would be to subclass the `Session` class to override
`rebuild_method`, but this means limits the plugin to only be able to use the
`Session` interface, and users won't be able to use this plugin for single
requests by providing an argument to `auth=`.

I couldn't find a way to reference the session from a given request, so I can't
dynamically patch the `Session` in use.

### Alternative: Subclassing `PreparedRequest`

I also explored subclassing `PreparedRequest` when `Auth`'s `__call__` method
is called, to try an influence the `copy()` method of `PreparedRequest`, but
that doesn't work for two reasons.

Firstly, in `PreparedRequest.prepare_auth()`, they call `auth()`, and then
update the results of the returned instance into the original, which means the
type of the instance that is used does not change from `PreparedRequest`.

Also, in `Session.resolve_redirects()`, the redirect target is separately
computed using `resp`, and the `PreparedRequest` (`req`) does not have any
access to that information. The copy of `req` then goes on to have its `url`
field populated from the separately-computed redirect target later.
