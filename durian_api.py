import requests


BASE = "https://api.durianrcs.com/out/ext_api"


def get_number(name, api_key, country, pid=1):
    url = f"{BASE}/getMobile"
    params = {
        "name": name,
        "ApiKey": api_key,
        "cuy": country,
        "pid": pid,
        "num": 1,
        "serial": 2
    }

    r = requests.get(url, params=params)
    return r.json()


def get_sms(name, api_key, phone, pid=1):
    url = f"{BASE}/getMsg"
    params = {
        "name": name,
        "ApiKey": api_key,
        "pn": phone,
        "pid": pid,
        "serial": 2
    }

    r = requests.get(url, params=params)
    return r.json()
