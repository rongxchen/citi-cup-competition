import json
import hashlib
import hmac


"""
encryption method used by qichacha,
all codes below from online and made a bit changes
"""


req_url = "/api/bigsearch/newsList?pageIndex=1&pageSize=20&searchKey=%E7%BE%8E%E5%9B%A2%20ESG"
req_data = {}
win_tid = 'e5493ee06b221db16de4ac9e9223f9d3'


def seeds_generator(s):
    seeds = {
        "0": "W",
        "1": "l",
        "2": "k",
        "3": "B",
        "4": "Q",
        "5": "g",
        "6": "f",
        "7": "i",
        "8": "i",
        "9": "r",
        "10": "v",
        "11": "6",
        "12": "A",
        "13": "K",
        "14": "N",
        "15": "k",
        "16": "4",
        "17": "L",
        "18": "1",
        "19": "8"
    }
    seeds_n = len(seeds)

    if not s:
        s = "/"
    s = s.lower()
    s = s + s

    res = ''
    for i in s:
        res += seeds[str(ord(i) % seeds_n)]
    return res


def a_default(url: str = '/', data=None):
    if data is None:
        data = {}
    url = url.lower()
    dataJson = json.dumps(data, ensure_ascii=False, separators=(',', ':')).lower()

    hashed = hmac.new(
        bytes(seeds_generator(url), encoding='utf-8'),
        bytes(url + dataJson, encoding='utf-8'),
        hashlib.sha512
    ).hexdigest()
    return hashed.lower()[8:28]


def r_default(url: str = '/', data=None, tid: str = ''):
    if data is None:
        data = {}
    url = url.lower()
    dataJson = json.dumps(data, ensure_ascii=False, separators=(',', ':')).lower()

    payload = url + 'pathString' + dataJson + tid
    key = seeds_generator(url)

    hashed = hmac.new(
        bytes(key, encoding='utf-8'),
        bytes(payload, encoding='utf-8'),
        hashlib.sha512
    ).hexdigest()
    return hashed.lower()
