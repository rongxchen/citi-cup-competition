import datetime
from urllib.parse import quote
import requests

from web_crawler.stock_news import qcc_enc
from web_crawler.utils import get_random_ua, get_random_proxy


"""
ip will be blocked by QCC :)
"""


class QCC:
    def __init__(self, search_key):
        self.page = 1
        self.headers = {
            "cookie": "acw_tc=70308d9a16731014293197612e3c8f9fb48e69c6a527d1444b7c1c7d6b; "
                      "QCCSESSID=338bc8f450044eb9be00ee8049; "
                      "qcc_did=bffd0e0e-9d21-4840-b4fa-8a25adc1674c; "
                      "UM_distinctid=1858c9dd0b1103c-04d16e7920ff9e-26021151-c4acd-"
                      "1858c9dd0b21041; "
                      "CNZZDATA1254842228=1192748805-1673098755-https%253A%252F%252"
                      "Fwww.baidu.com%252F%7C1673098755",
            "user-agent": get_random_ua(),
        }
        self.search_key = search_key

    def get_news(self, size=50):
        result_list = {"news": [], "ratings": []}

        # size control and proxy selection (randomly)
        size = 90 if size > 90 else size
        proxy = get_random_proxy()
        print(f"ip address now: {proxy}")

        # url and request header completion
        url = f"https://www.qcc.com/api/bigsearch/newsList?" \
              f"pageIndex={self.page}&pageSize={size}&searchKey={quote(self.search_key)}"
        request_url = "/api" + url.split("/api")[1]
        self.headers[qcc_enc.a_default(request_url, {})] = \
            qcc_enc.r_default(request_url, {}, 'b4440df7920b58e9cac43fef2d67d1ae')

        try:
            resp = requests.get(url=url, headers=self.headers, proxies=proxy,
                                allow_redirects=False, timeout=10)
            if resp.status_code != 200:
                # return self.get_news()
                print("qcc status code problem: " + resp.text)
                return result_list
        except Exception as ex:
            print(ex)
            # return self.get_news()
            return result_list

        json = resp.json()
        if "Result" not in json or "Paging" not in json or "GroupItems" not in json:
            print("qcc json problem: " + str(json))
            return result_list

        # get total number of records
        total_records = json["Paging"]["TotalRecords"]
        print(f"There are {total_records} records in total\n")

        # get number of records by category (e.g., positive, neutral, negative)
        sentiment = json["GroupItems"][0]["items"]
        other_sentiment = json["GroupItems"][2]["items"]
        count_list = {}
        for s in sentiment:
            count_list[s["desc"]] = s["count"]
        for o in other_sentiment:
            count_list[o["desc"]] = o["count"]
        result_list["ratings"] = count_list

        # get new list
        news_list = json["Result"]
        # Id, Title, Event, Content, PublishTime, Source, SourceUrl, Score, Impact,
        # ImpactDesc, Tags, TagsDesc, TopicsDesc, Keyword, Relations, TagsNew, SimilarCount
        for news in news_list:
            title = news["Title"].replace("<em>", "").replace("</em>", "")
            content = news["Content"][0].replace("<em>", "").replace("</em>", "")
            publish_time = datetime.datetime.fromtimestamp(int(news["PublishTime"])).date()
            # source = news["Source"]
            source_url = news["SourceUrl"]
            score = news["Score"]
            impact = news["ImpactDesc"]
            # temp = [title, content, str(publish_time), source, source_url, score, impact]
            temp = {"title": title, "date": str(publish_time), "url": source_url,
                    "score": round(float(score), 1), "impact": impact}
            result_list["news"].append(temp)

        return result_list
