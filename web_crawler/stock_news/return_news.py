import datetime
import requests
import json
import re
from bs4 import BeautifulSoup

from web_crawler.utils import get_random_ua, get_random_proxy


def sina_esg_news(page=1, size=10, cid=244215):
    """ get esg top news from sina (CHIN version)
    :param page: no. of page
    :param size: no. of page size
    :param cid: special id for querying different kinds of ESG news in sina api
    :return: list of news
    """
    top_news = {"news": [], "total": 0}

    timestamp = int(datetime.datetime.now().timestamp())
    # cid
    # top news: 244215
    # investment: 248417
    # E: 247831
    # S: 247832
    # G: 247833
    url = "https://interface.sina.cn/finance/column/esg/article_api.d.json?" \
          f"cid={cid}&page={page}&pagesize={size}&callback=sinajp_{timestamp}"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    text = requests.get(url=url, headers=headers, proxies=proxies).text
    result = json.loads(text[text.find("{"):text.rfind("}")+1])["result"]
    data = result["data"]
    top_news["total"] = result["total_number"]
    for d in data:
        print(d)
        title = d["title"]
        url = d["url"]
        publish_time = d["pub_time"]
        source = d["media"]
        pic_url = d["thumb"]
        top_news["news"].append({"title": title, "publish_time": publish_time,
                                 "source": source, "url": url, "pic_url": pic_url})
    return top_news


def return_eng_top_news():
    """ get ESG top news (ENG version) from https://esgnews.com/
    :return: list of news
    """
    url = "https://esgnews.com/"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()
    resp = requests.get(url=url, headers=headers, proxies=proxies)

    html = BeautifulSoup(resp.text, "html.parser")
    find_title = re.compile(r'<a class="tt-post-title c-h5" href="(.*?)">(.*?)</a>')
    find_description = re.compile(r'<span class="tt-post-author-name"><a href=".*?">(.*?)</a></span>')
    find_date = re.compile(r'<span class="tt-post-date">(.*?)</span>')
    find_pic = re.compile(r'<img.*?src="(.*?)".*?>')

    news_list = html.select(".tt-post")

    return_list = []
    for news in news_list:
        title = re.findall(find_title, str(news))
        description = re.findall(find_description, str(news))
        date = re.findall(find_date, str(news))
        pic_url = re.findall(find_pic, str(news))
        if title and description and date and pic_url:
            return_list.append({"title": title[0][1].replace("<small>", "").replace("</small>", ""),
                                "description": description[0],
                                "url": title[0][0], "pic_url": pic_url[0], "date": date[0]})
    return return_list


def return_eng_top_news_from_scmp():
    """ get ESG top news (ENG version) 2 from scmp
    :return: list of news
    """
    return_list = []
    url = "https://www.scmp.com/topics/esg-investing"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()
    resp = requests.get(url=url, headers=headers, proxies=proxies)

    html = BeautifulSoup(resp.text, "html.parser")
    news_list = html.select("div.ef7usvb7.css-10lo5g6.eitxwtf8")
    host_url = "https://www.scmp.com"
    for n in news_list:
        title = n.select("span.css-0.e1tw0x8h0")[0].text
        description = n.select("p.css-542wex.e1rrdxfy0")[0].text
        url = host_url + n.select("a")[0]["href"]
        date = n.select("time")[0].text.split(" - ")[0]
        pic_url = n.select("img")[0]["src"]
        if len(description) > 40:
            description = description[: 40]+"..."
        news = {"title": title, "description": description, "url": url, "pic_url": pic_url, "date": date}
        return_list.append(news)

    return return_list
