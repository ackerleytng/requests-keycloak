from autologin import AutoLoginSession


with AutoLoginSession() as s:
    r = s.get("https://httpbin.localhost/get", verify=False)
    print(r.text)
