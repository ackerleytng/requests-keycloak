from requests_keycloak import KeycloakSession


with KeycloakSession() as s:
    r = s.get("https://httpbin.localhost/get", verify=False)
    print(r.text)
