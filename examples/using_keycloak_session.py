from requests_keycloak import KeycloakSession

from utils import dump


with KeycloakSession() as s:
    r = s.get("https://httpbin.localhost/get", verify=False)
    dump(r)

    print()
    print("No further logins, since the same KeycloakSession is shared")

    r = s.get("https://httpbin.localhost/get", verify=False)
    dump(r)
