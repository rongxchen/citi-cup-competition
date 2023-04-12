# import os.path
# import re
import datetime
import json
import requests
import urllib.request
import urllib.error
from datetime import date
from dateutil.relativedelta import relativedelta

from web_crawler.utils import get_random_ua, get_random_proxy


def get_sse_notice(security_code, key_word, years=3):
    """ get shanghai listed company notices from sse website
    :param security_code: stock code
    :param key_word: keyword for filtering the title of notices
    :param years: interval of years
    :return: list of notices
    """
    result = []

    end_date = date.today()
    timestamp = datetime.datetime.now().timestamp()
    proxies = get_random_proxy()
    response = requests.get(
        url='http://query.sse.com.cn/security/stock/queryCompanyBulletinNew.do?'
            'jsonCallBack=jsonpCallback78837799&isPagination=true&pageHelp.pageSize=100&pageHelp.cacheSize=1&'
            'START_DATE=' + str(end_date-relativedelta(years=years)) + '&END_DATE=' + str(end_date) +
            f'&SECURITY_CODE=' + security_code + '&TITLE=' + key_word + f'&BULLETIN_TYPE=&stockType=&_={timestamp}',
        headers={'Referer': 'http://www.sse.com.cn/disclosure/listedinfo/regular/',
                 "user-agent": get_random_ua()},
        proxies=proxies
    )

    text = response.text
    json_str = text[text.find("{"):text.rfind("}")+1].replace("null", "")
    data = eval(json_str)

    for report in data['result']:
        for item in report:
            result.append({'title': item['TITLE'],
                           'date': item['URL'].split('/')[-2],
                           'url': 'http://static.sse.com.cn/' + item['URL'],
                           'description': item["BULLETIN_TYPE_DESC"]
                           })
            # Please uncomment the following codes if you want to find the annual report
            # if re.search('年度报告', item['TITLE'], re.S):
            #     if re.search('摘要', item['TITLE'], re.S):
            #         pass
            #     else:
            #         result.append({'title': item['TITLE'],
            #                        'date': item['URL'].split('/')[-2],
            #                        'url': 'http://static.sse.com.cn/' + item['URL'],
            #                        'description': '年报'
            #                        })
            #
            #         #Please uncomment the following codes if you want to download the found PDF file directly
            #         filename = item['TITLE'] + item['URL'].split('/')[-2] + '.pdf'
            #         if re.search('ST', item['TITLE'], re.S):
            #             filename = '-ST' + item['URL'].split('/')[-2] + '.pdf'
            #         resource = requests.get(result[-1]['url'], stream=True)
            #         with open(filename, 'wb') as fd:
            #             for y in resource.iter_content(102400):
            #                 fd.write(y)
            #             print(filename, 'Download Complete')

    return result


def askURL(url):
    """ tool function using for fetching hk notices
    :param url: url
    :return: json formatted string
    """
    headers = {"User-Agent": get_random_ua()}
    request = urllib.request.Request(url=url, headers=headers)
    proxy_handler = urllib.request.ProxyHandler(get_random_proxy())
    opener = urllib.request.build_opener(proxy_handler)
    try:
        response = opener.open(request)
        return response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        return ""


file_name = "C:\\Users\\chenr\\PycharmProjects\\Citi\\web_crawler\\stock_notice\\hkse_stock_id.json"


def get_hkse_notice(stock_code, keyword="", year=3):
    """ get hkse listed company notices from hkse
    :param stock_code: stock code of the company
    :param keyword: keyword for filtering title
    :param year: interval of years
    :return: list of notices
    """
    with open(file_name, "r") as file:
        id_list = json.loads(file.read())

    date = datetime.date.today()
    start = date - datetime.timedelta(days=365*year)
    end = "".join(str(date).split("-"))
    stock_id = id_list[stock_code]
    URL = "https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0" \
          f"&market=SEHK&stockId=" + str(stock_id) + f"&documentType=-1&fromDate={start}&toDate={end}&title={keyword}&" \
          "searchType=1&t1code=40000&t2Gcode=-2&t2code=-2&rowRange=400&lang=zh"
    html = askURL(URL)
    html = html.replace('\\', '')

    L = []
    pair = []
    for i in range(len(html)):
        if html[i] == '[':
            L.append(i)
        elif html[i] == ']':
            pair.append([L[len(L)-1], i])
            L.pop(len(L)-1)
        else:
            continue
    html = html[pair[-3][0]:pair[-3][1]+1]
    html = json.loads(html)

    final_res = []
    for i in html:
        now = {"title": i['TITLE'].replace("u0026#x2f", ""), 'date': i['DATE_TIME'].split(' ')[0],
               'url': "https://www1.hkexnews.hk" + i['FILE_LINK'],
               'description': i['LONG_TEXT'].split(' ')[0].replace("u0026#x2f", "").replace(";", "; ")}
        final_res.append(now)

    return final_res


# def get_id():
#     URL = "https://www1.hkexnews.hk/ncms/script/eds/activestock_sehk_c.json?_=1675993149142" #id code pair
#     result = askURL(URL)
#     p1 = re.compile(r'[{](.*?)[}]', re.S)
#     result = re.findall(p1,result)
#     final_result = []
#     for i in result:
#         a = json.loads("{"+i+"}")
#         final_result.append(a)
#     ans = {}
#     for i in final_result:
#         ans[i['c']]=i['i']
#     return ans


def cninfo_notice(stock_code, exchange, search_key="", size=30, years=5):
    """ get szse listed company notices from cninfo
    :param stock_code: stock code of the company
    :param exchange: i.e., SZSE, as it can fetch notices from SZSE/SSE/HKSE market
    :param search_key: keyword for filtering title/content of the notices
    :param size: no. of page size
    :param years: interval of years
    :return: list of notices
    """
    end = datetime.datetime.now().date()
    start = end - datetime.timedelta(days=365*years)

    ex = "hke" if exchange == "HKSE" else "szse"
    file_name = f"C:\\Users\\chenr\\PycharmProjects\\Citi\\web_crawler\\stock_notice\\cninfo_{ex}_list.json"
    org_id = ""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            stock_list = json.loads(file.read())["stockList"]
            for stk in stock_list:
                if stk["code"] == stock_code:
                    org_id = stk["orgId"]
                    break
    except Exception as e:
        print(f"exception: {e}")
        print("error occurred in cninfo json parse")

    def abs_url(stock_code, announcement_id, org_id, announcement_time):
        return f"http://www.cninfo.com.cn/new/disclosure/detail?stockCode={stock_code}&" \
               f"announcementId={announcement_id}&orgId={org_id}&announcementTime={announcement_time}"

    data = {
        "pageNum": "1",
        "pageSize": size,
        "column": "hke" if exchange == "HKSE" else "szse",
        "category": "",
        # "category": "" if exchange == "HKSE" else "category_ndbg_szsh;category_bndbg_szsh;category_yjdbg_szsh;"
        #                                              "category_sjdbg_szsh;category_rcjy_szsh;category_gszl_szsh;"
        #                                              "category_qtrz_szsh;category_fxts_szsh",
        "stock": f"{stock_code},{org_id}" if org_id != "" else "",
        "tabName": "fulltext",
        "searchkey": search_key,
        "seDate": f"{start}~{end}",
        "isHLtitle": "true"
    }

    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {"user-agent": get_random_ua()}
    proxies = get_random_proxy()

    print(data)
    try:
        resp = requests.post(url=url, headers=headers, data=data, proxies=proxies)
        announcements = resp.json()["announcements"]
        if announcements is None:
            return []
    except Exception as e:
        print(f"exception: {e}")
        return []

    result_list = []
    for announcement in announcements:
        code = announcement["secCode"]
        aid = announcement["announcementId"]
        title = announcement["announcementTitle"].replace("<em>", "").replace("</em>", "")
        time = datetime.datetime.fromtimestamp(int(announcement["announcementTime"])/1000)
        sec_name = announcement["secName"].replace("<em>", "").replace("</em>", "")
        temp_lst = {"title": title,
                    "url": abs_url(code, aid, org_id, str(time.date())),
                    "description": "公告",
                    "date": str(time).split(" ")[0]}
        result_list.append(temp_lst)

    return result_list
