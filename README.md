# requests-keycloak

Makes requests take the role of a User-Agent (as defined in the OAuth 2.0
world), automatically logs in to keycloak using a username and password
configured as environment variables.

requests-keycloak is intended as a stopgap replacement for the use of API keys,
where the API keys are meant to both authenticate and provide authorization in
the OAuth world.

## Usage

Without requests-keycloak, you would have done

```
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
>>> import requests
>>> r = requests.get('https://api.github.com/repos/psf/requests')
>>> r.json()["description"]
'A simple, yet elegant HTTP library.'
```

With requests-keycloak,

```
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
>>> import requests
>>> r = requests.get('https://secured.example/keycloak/protected/endpoint, auth=KeycloakAuth())
>>> r.json()["description"]
'Convenient!'
```

Or try our examples!

## Examples

Start the dev environment

```
$ cd dev-environment
$ docker-compose up -d  # Starts keycloak, creates a OAuth client for httpbin
```

Try accessing

```
https://httpbin.localhost/anything
```

in your browser - you'll have to login with `user0` and `password`, and you'll
have to change your password.

Run the examples:

```
AUTOLOGIN_USERNAME=user0 AUTOLOGIN_PASSWORD=password python examples/using_keycloak_auth.py
```

```
AUTOLOGIN_USERNAME=user0 AUTOLOGIN_PASSWORD=password python examples/using_keycloak_session.py
```

```
AUTOLOGIN_USERNAME=user0 AUTOLOGIN_PASSWORD=password python examples/using_keycloak_session_post.py
```
