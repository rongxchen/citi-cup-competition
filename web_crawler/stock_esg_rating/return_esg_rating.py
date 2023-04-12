import requests
import datetime
import json

from web_crawler.utils import get_random_ua, get_random_proxy


def from_sina_finance(ticker):
    """ get all esg ratings from different agencies using sina api
    :param ticker: stock ticker
    :return: all ratings without empty rating result (i.e., after data filtering)
    """
    rating_list = {"ratings": [], "total": 0}

    timestamp = int(datetime.datetime.now().timestamp())
    ticker = str(ticker)
    url = "https://global.finance.sina.com.cn/api/openapi.php/EsgService.getEsgStockInfo?" \
          f"symbol={ticker}&callback=sinajp_{timestamp}"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies)
        resp = resp.text
        data = json.loads(resp[resp.find("{"):resp.rfind("}")+1])["result"]["data"]["info"]
        for d in data:
            agency = d["agency_name"]
            date = d["esg_dt"]
            score = d["esg_score"]
            level = d["esg_level"]
            if score != "-":
                rating_list["ratings"].append(
                    {"agency": agency, "score": score, "level": level, "date": date}
                )
        rating_list["total"] = len(rating_list["ratings"])
    except Exception as ex:
        print(f"exception: {ex}")
        print("error occurred in rating > sina finance")

    return rating_list
