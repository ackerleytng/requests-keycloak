# This is just sample code, do not disable warnings in production!
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def dump(response):
    print(f"response.status_code: {response.status_code}")
    print("response.history:")
    for r in response.history:
        print("  " + r.url)

    print("  " + response.url)
