import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from web_crawler.utils import get_random_ua, get_random_proxy


def stock_info_from_futu_html(code, market: str):
    data = {}

    exchange = "HK" if market == "HKSE" else ("SH" if market == "SSE" else "SZ")
    timestamp = datetime.now().timestamp()

    chin2eng = {
        "成交额": "volume_dollar",
        "成交量": "volume_no",
        "总市值": "market_value",
        "市盈率TTM": "PE_TTM",
        "市净率": "PB"
    }

    url = f"https://www.futunn.com/stock/{code}-{exchange}?_ftsdk={timestamp}"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        html = BeautifulSoup(resp.text, "html.parser")
        stock_detail_li_list = html.find_all(class_="stock-detail-li")
        curr_price = html.find_all(class_="stock-price ellipsis")

        find_k_v = re.compile('<div.*?><div.*?>(.*?)</div><div.*?>(.*?)</div></div>')
        if len(curr_price) > 0:
            price = curr_price[0].text
        else:
            price = 0
        data["curr_price"] = price

        for sdl in stock_detail_li_list:
            kv = re.findall(find_k_v, str(sdl))
            if len(kv) == 0:
                continue
            kv = kv[0]
            if len(kv) > 0 and kv[0] in chin2eng and kv[-1] != "--":
                # data[chin2eng[kv[0]]] = {kv[0]: kv[-1]}
                data[chin2eng[kv[0]]] = kv[-1]
    except Exception as e:
        print(e)
        print("error occurred in fetching futu data")

    key_indicators = key_indicator_from_futu_html(code, market)
    for ki in key_indicators:
        data[ki] = key_indicators[ki]
    return data


def key_indicator_from_futu_html(code, market):
    data = {}

    chin2eng = {
        "基本每股收益（元）": "eps",
        "净资产收益率(ROE)": "return_on_equity",
        "总资产净利率(ROA)": "return_on_asset",
        "资产负债率": "asset_liability_ratio",
        "流动比率": "liquid_ratio",
        "净资产收益率_加权,公布值": "return_on_equity",
        "总资产净利率": "return_on_asset"
    }

    exchange = "HK" if market == "HKSE" else ("SH" if market == "SSE" else "SZ")
    url = f"https://www.futunn.com/stock/{code}-{exchange}/key-indicators"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        html = BeautifulSoup(resp.text, "html.parser")
        title_list = html.find_all(class_="value time-value")[0]
        child_item_list = html.find_all(class_="child-item")

        find_k_v = re.compile('<div.*?><span.*?title="(.*?)">.*?</span><div.*?><span.*?><span.*?>.*?</span>'
                              '<span.*?>(.*?)</span></span><span.*?><span.*?>.*?</span>'
                              '<span.*?>(.*?)</span></span><span.*?><span.*?>.*?</span>'
                              '<span.*?>(.*?)</span></span><span.*?><span.*?>.*?</span>'
                              '<span.*?>(.*?)</span></span></div></div>', re.S)
        find_titles = re.compile(r'<span data-v-fcb69b0e="">(.*?)</span>', re.S)
        titles = re.findall(find_titles, str(title_list))

        for ci in child_item_list:
            kv = re.findall(find_k_v, str(ci))
            if len(kv) == 0:
                continue
            kv = kv[0]
            if len(kv) > 0 and kv[0] in chin2eng and kv[-1] != "--":
                # data[chin2eng[kv[0]]] = {kv[0]: kv[-1]}
                data[chin2eng[kv[0]]] = kv[-1]
    except Exception as e:
        print(e)
        print("error occurred in fetching futu data")

    return data
