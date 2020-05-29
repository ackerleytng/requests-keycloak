import requests

from requests_keycloak import KeycloakAuth

from utils import dump


r = requests.get("https://httpbin.localhost/get", auth=KeycloakAuth(), verify=False)
dump(r)

print()
print("Notice how you have to login again with the second requests.get()")


r = requests.get("https://httpbin.localhost/get", auth=KeycloakAuth(), verify=False)
dump(r)

print()
print("Use a KeycloakSession to share the same session (save logins)")
