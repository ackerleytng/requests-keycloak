from requests_keycloak import KeycloakSession

from utils import dump


with KeycloakSession() as s:
    r = s.post("https://httpbin.localhost/anything", verify=False)
    dump(r, full=True)
