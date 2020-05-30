# This is just sample code, do not disable warnings in production!
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _dump(r):
    print(f"  {r.status_code} {r.request.method} {r.url}")

def dump(response, full=False):
    if full:
        print(f"response.text:")
        print(response.text)

    print(f"response.status_code: {response.status_code}")
    print("response.history:")
    for r in response.history:
        _dump(r)

    _dump(response)
