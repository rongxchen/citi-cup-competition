import datetime
import os.path

import requests
import json

from web_crawler.utils import get_random_ua, get_random_proxy
from web_crawler.esg_score_by.return_msci_sectors import return_score_by_sector


def get_sector(stock_code: str, exchange: str):
    data = ""

    if exchange == "HKSE":
        symbol = stock_code.lstrip("0")
        timestamp = datetime.datetime.now().timestamp()
        url = f"https://www1.hkex.com.hk/hkexwidget/data/getequityquote?sym={symbol}&token=evLtsLsBNAUVTPxtGqVeG7Ovi54ZCOr8Mhz78GuUU3UPfMDuKKnGHBiIcHkd5fsl&lang=eng&qid={timestamp}&callback=jQuery35106461294954516379_{timestamp-20000}&_={timestamp-19999}"
        headers = {"user-agent": get_random_ua()}
        proxies = get_random_proxy()

        try:
            resp = requests.get(url=url, headers=headers, proxies=proxies).text
            json_data = json.loads(resp[resp.find("{"):resp.rfind("}")+1])
            data = json_data["data"]["quote"]["csic_classification"]
            if data is None:
                data = json_data["data"]["quote"]["hsic_ind_classification"]

            if data.startswith("Telecommunication"):
                data = "Communication Services"

            if "-" in data:
                data = data.split("-")[0].strip()

        except Exception as e:
            print(e)

    sector_detail = {}
    curdir = os.getcwd()
    with open(f"{curdir}/web_crawler/esg_score_by/data/sector_subsector_score_list.json", "r") as file:
        sector_list = json.loads(file.read())
        for sector in sector_list:
            if sector["name"] == data:
                id = sector["id"]
                sector_detail = {"industry": sector["name"], "detail": return_score_by_sector(id)}
                return sector_detail

    return {}
