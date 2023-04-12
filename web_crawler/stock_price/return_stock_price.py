import datetime
import json
import yfinance
import requests
import re
from bs4 import BeautifulSoup

from web_crawler.utils import get_random_ua, get_random_proxy


def hk_price_from_futu(code, market):
    data = []

    exchange = "HK" if market == "HKSE" else ("SH" if market == "SSZ" else "SZ")

    index_url = f"https://www.futunn.com/stock/{code}-{exchange}"
    headers = {"user-agent": get_random_ua(),
               "cookie": "cipher_device_id=1678782273167608; device_id=1678782273167608; sajssdk_2015_cross_new_user=1; locale=zh-cn; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22ftv1fuZQhf8%2FBXyyRkRWPdMTVY7c%2Fzedl%2Bkg2S5kgqMo8TOO7HsZK9%2FkdQM%2BzZrjRYZo%22%2C%22first_id%22%3A%22186df3897e6349-0ac1b401f76e7a-26031851-805581-186df3897e730e%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfbG9naW5faWQiOiJmdHYxZnVaUWhmOC9CWHl5UmtSV1BkTVRWWTdjL3plZGwra2cyUzVrZ3FNbzhUT083SHNaSzkva2RRTSt6WnJqUllabyIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODZkZjM4OTdlNjM0OS0wYWMxYjQwMWY3NmU3YS0yNjAzMTg1MS04MDU1ODEtMTg2ZGYzODk3ZTczMGUifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22ftv1fuZQhf8%2FBXyyRkRWPdMTVY7c%2Fzedl%2Bkg2S5kgqMo8TOO7HsZK9%2FkdQM%2BzZrjRYZo%22%7D%2C%22%24device_id%22%3A%22186df3897e6349-0ac1b401f76e7a-26031851-805581-186df3897e730e%22%7D; futunn_lang=zh-CN; search_keyword=09988; quote-csrf=oA4LX6wYHlBSV66D5HTFl2n8ufk=; Hm_lvt_f3ecfeb354419b501942b6f9caf8d0db=1678782286; _gid=GA1.2.1151494923.1678782287; ftreport-jssdk%40session={%22distinctId%22:%22ftv1fuZQhf8/BXyyRkRWPdMTVY7c/zedl+kg2S5kgqMo8TOO7HsZK9/kdQM+zZrjRYZo%22%2C%22firstId%22:%22ftv1fuZQhf8/BXyyRkRWPdMTVY7c/zedl+kg2S5kgqMo8TOO7HsZK9/kdQM+zZrjRYZo%22%2C%22latestReferrer%22:%22https://www.futunn.com/quote/cn%22}; Hm_lpvt_f3ecfeb354419b501942b6f9caf8d0db=1678785090; _ga_EJJJZFNPTW=GS1.1.1678784892.2.1.1678785090.0.0.0; _ga=GA1.1.1257798275.1678782287; _ga_XECT8CPR37=GS1.1.1678784892.2.1.1678785090.0.0.0",
               "futu-x-csrf-token": "p3oHyED9DxWC3SUjj5U1zA==-dvvSK6DZG6y7IDxonkCPi5QHfMs="}
    proxies = get_random_proxy()

    stock_id = ""
    try:
        resp = requests.get(url=index_url, headers=headers, proxies=proxies)
        html = BeautifulSoup(resp.text, "html.parser")
        find_required_url = re.compile(r'<a.*?href=".*?ns_stock_id=(.*?)&.*?target="_blank">')
        stock_id = re.findall(find_required_url, str(html.find_all(class_="news-item")[0]))
        if len(stock_id) == 0:
            return []
        stock_id = stock_id[0]
    except Exception as e:
        print(e)

    # market_type:
    market_type = "1" if market == "HKSE" else ("4" if market == "SSE" or market == "SZSE" else "")
    # type = 2 if kline is in daily
    kline_type = 2
    url = f"https://www.futunn.com/quote-api/get-kline?stock_id={stock_id}&market_type={market_type}&type={kline_type}"

    try:
        price_data = requests.get(url=url, headers=headers, proxies=proxies).json()["data"]["list"][-366:]
        for price in price_data:
            date = datetime.datetime.fromtimestamp(price["k"])
            data.append({"date": str(date.date()), "value": float(price["c"])})
    except Exception as e:
        print(e)

    return data


def hk_stock_price(ticker, start, end, interval):
    data = []

    try:
        prices = yfinance.download(tickers=ticker, start=start, end=end, interval=interval).reset_index()
        adj_close = prices[["Date", "Adj Close"]].values
        for ac in adj_close:
            date = str(ac[0]).split(" ")[0]
            value = ac[1]
            data.append({"date": date, "value": value})
    except Exception as e:
        print(e)
        print("error occurred in fetching hk stock price with yfinance")

    return data


def sz_stock_price(stock_code):
    url = "http://www.szse.cn/api/market/ssjjhq/getHistoryData?random=0.20940211576825507&cycleType=32" \
          f"&marketId=1&code={stock_code}"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    data = []

    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        prices = resp.json()["data"]["picupdata"]
        for p in prices:
            data.append({"date": p[0], "value": float(p[2])})
    except Exception as e:
        print(e)

    return data


def sh_stock_price(stock_code):
    timestamp = datetime.datetime.now().timestamp()
    url = f"http://yunhq.sse.com.cn:32041/v1/sh1/dayk/{stock_code}?callback=jQuery112402981150239609356_{timestamp}&begin=-730&end=-1&period=day&_={timestamp}"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    data = []

    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        text = resp.text
        prices = json.loads(text[text.find("{"):text.rfind("}")+1])["kline"]
        for p in prices:
            date = str(p[0])
            date = date[:4] + "-" + date[4:6] + "-" + date[6:]
            data.append({"date": date, "value": float(p[4])})
    except Exception as e:
        print(e)

    return data

