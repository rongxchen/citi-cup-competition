from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

import os
import json
import datetime

from web_crawler.stock_code.return_code import return_sse_stock, return_szse_stock, return_hk_stock
from web_crawler.stock_news.qcc import QCC
from web_crawler.stock_news.return_news import sina_esg_news, return_eng_top_news
from web_crawler.stock_esg_rating.return_esg_rating import from_sina_finance
from web_crawler.esg_score_by.return_msci_sectors import return_sector_subsector_list, return_score_by_sector, return_score_by_subsector
from web_crawler.esg_score_by.classifier import get_sector
from web_crawler.stock_notice.return_notice import get_hkse_notice, cninfo_notice
from web_crawler.financial_data.get_fin import hk_analysis
from web_crawler.financial_data.futu import stock_info_from_futu_html
from web_crawler.stock_price.return_stock_price import hk_stock_price, hk_price_from_futu, sz_stock_price, sh_stock_price
from web_crawler.utils import youdao_translator


"""
use absolute path for all file names
append absolute path if necessary
"""
import sys
curdir = os.getcwd()
sys.path.append(f"{curdir}\\nlp_tool")
from nlp_tool.citi_emotion_analysis import emotion_detection


def Result(code: int, data: any, success: bool, msg: str):
    """
    :param code: message code of fetched data
    :param data: in list/dict
    :param success: whether it is successfully fetched data
    :param msg: just a message
    :return: encapsulated result in json format(i.e., dict in python)
    """
    return {"code": code, "data": data, "success": success, "msg": msg}


class Code:
    """
    message codes
    """
    GET_OK = 20000
    GET_OK_BUT_EMPTY = 20001
    GET_ERR = 40000


def return_message(code, item):
    """
    :param code: message code
    :param item: metadata of returned data
    :return: a string (i.e., message)
    """
    if code == Code.GET_OK:
        msg = f"{item} found"
    elif code == Code.GET_OK_BUT_EMPTY:
        msg = f"no {item} found"
    elif code == Code.GET_ERR:
        msg = "error occurred in backend"
    else:
        msg = ""
    return msg


"""""""""""""""""""""
"""""""""""""""""""""
"controllers below"""
"""""""""""""""""""""
"""""""""""""""""""""


def home(request):
    """ path to the home page
    :param request: none
    :return: to the home page
    """
    return render(request, "companies/index.html")


def get_company_and_exchange(request, ticker: str, exchange: str):
    """ get companies details by stock code / company name & exchange
    :param request: none
    :param ticker: stock code
    :param exchange: exchange it belongs to
    :return: details of found companies
    """
    ticker = ticker.strip()
    exchange = exchange.lower()
    stock_list = []

    try:
        if exchange == "sse":
            stock_list = return_sse_stock(ticker)["codes"]
        elif exchange == "szse":
            stock_list = return_szse_stock(ticker)["codes"]
        elif exchange == "hkse":
            stock_list = return_hk_stock(ticker)["codes"]
        else:
            stock_list = return_sse_stock(ticker)["codes"] + return_szse_stock(ticker)["codes"] + \
                         return_hk_stock(ticker)["codes"]
        success = True
        code = Code.GET_OK if len(stock_list) > 0 else Code.GET_OK_BUT_EMPTY
    except Exception as ex:
        print(f"exception: {ex}")
        success = False
        code = Code.GET_ERR

    data = {"total": len(stock_list), "companies": stock_list}

    result = Result(code, data, success, return_message(code, "stock(s)"))
    return JsonResponse(data=result, safe=False)


def get_company(request, ticker: str):
    """ get companies details by ticker only
    :param request: none
    :param ticker: stock code
    :return: details of companies
    """
    return get_company_and_exchange(request, ticker, "all")


@csrf_exempt
def report_enterprise_news(request):
    """ get enterprise news data
    :param request: get POST data
    :return: news of a specific enterprise
    """
    news = {"enterprise": {"news": [], "ratings": {}}, "total": 0}

    try:
        company = json.loads(request.body.decode("utf-8"))  # must use json to parse, but not dict()
        data = QCC(search_key=company["name"]).get_news()
        news["enterprise"]["news"] = data["news"]
        news["enterprise"]["ratings"] = data["ratings"]
        news["total"] = len(news["enterprise"]["news"])
        code = Code.GET_OK if len(news["enterprise"]["news"]) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as ex:
        code = Code.GET_ERR
        success = False
        print(f"exception: {ex}")
        print("error occurred during fetching news data")

    result = Result(code, news, success, return_message(code, "enterprise news"))
    return JsonResponse(data=result, safe=False)


def top_news(request, cid, page, page_size):
    """ get general top news data in CHIN version
    :param request: none
    :param cid: parameter of sina's api (i.e., types of top news, e.g., economic, social, governance)
    :param page: no. of page
    :param page_size: no. of page size
    :return: general top news about ESG
    """
    news = {"top_news": {"list": [], "cur_size": 0}, "total": 0, "emotion": {"list": [], "pos": 0, "neu/neg": 0}}

    try:
        n = sina_esg_news(page, page_size, cid)
        news["top_news"]["list"] = n["news"]
        news["top_news"]["cur_size"] = len(news["top_news"]["list"])
        news["total"] = n["total"]
        titles = ""
        for t in news["top_news"]["list"]:
            titles += t["title"] + "/|\\"
        translated_words = youdao_translator(titles[:titles.rfind("/")]).split(" / | \\ ")
        nlp_scores = nlp_analysis(translated_words)
        for t in range(len(translated_words)):
            print(f"new sentence: {translated_words[t]}")
            print(f"score: {nlp_scores[t]}")
        news["emotion"]["list"] = nlp_scores
        news["emotion"]["pos"] = nlp_scores.count(1)
        news["emotion"]["neu/neg"] = nlp_scores.count(0)
        code = Code.GET_OK if news["top_news"]["cur_size"] > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as ex:
        code = Code.GET_ERR
        success = False
        print(f"exception: {ex}")
        print("error occurred during fetching top news data")

    result = Result(code, news, success, return_message(code, "top news"))
    return JsonResponse(data=result, safe=False)


def top_news_simple(request):
    """ get general news data in CHIN version
    :param request: none
    :return: general top news about ESG (default setting)
    """
    return top_news(request, "244215", 1, 10)


def top_news_eng(request):
    """ get general new data in ENG version
    :param request: none
    :return: general top news about ESG of ENG version (i.e., international news)
    """
    data = {"list": None, "total": 0, "emotion": {"list": [], "pos": 0, "neu/neg": 0}}

    try:
        data["list"] = return_eng_top_news()
        data["total"] = len(data["list"])
        titles = []
        for lst in data["list"]:
            titles.append(lst["title"])
        data["emotion"]["list"] = nlp_analysis(titles)
        data["emotion"]["pos"] = data["emotion"]["list"].count(1)
        data["emotion"]["neu/neg"] = data["emotion"]["list"].count(0)
        code = Code.GET_OK if data["total"] > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(f"exception: {e}")

    result = Result(code, data, success, return_message(code, "eng top news"))
    return JsonResponse(data=result, safe=False)


@csrf_exempt
def report_ratings(request):
    """ get ratings of a companies
    :param request: get POST data
    :return: ratings from different agencies (sina api)
    """
    ratings = {"ratings": [], "total": 0}

    try:
        stock = json.loads(request.body.decode("utf-8"))
        if stock["market"].upper() == "HKSE":
            ticker = "hk" + stock["code"]
        elif stock["market"].upper() == "SZSE":
            ticker = "sz" + stock["code"]
        else:
            ticker = "sh" + stock["code"]
        ratings = from_sina_finance(ticker)
        code = Code.GET_OK if len(ratings["ratings"]) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as ex:
        code = Code.GET_ERR
        success = False
        print(f"exception: {ex}")
        print("error occurred during fetching esg ratings")

    result = Result(code, ratings, success, return_message(code, "ratings"))
    return JsonResponse(data=result, safe=False)


def report_sector_subsector_list(request):
    """ get sector-subsector list
    :param request: none
    :return: list contains multiple key-values (i.e., {sector1: subsectors, sector2: subsectors})
    """
    data = []

    try:
        data = return_sector_subsector_list()
        code = Code.GET_OK if len(data) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(f"exception: {e}")
        print("error occurred in getting sub_sector_list")

    result = Result(code, data, success, return_message(code, "sector list"))
    return JsonResponse(data=result, safe=False)


def report_sector_score(request, sector_id):
    """ get scores by sector
    :param request: none
    :param sector_id: specify the sector id
    :return: scores by sector
    """
    data = {}

    try:
        data = return_score_by_sector(sector_id)
        not_empty = len(data["environment"]) > 0 or len(data["social"]) > 0 or len(data["governance"]) > 0
        code = Code.GET_OK if not_empty else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(f"exception: {e}")
        print("error occurred in getting by_sector")

    result = Result(code, data, success, return_message(code, "sector scores"))
    return JsonResponse(data=result, safe=False)


def report_sub_sector_score(request, subsector_id):
    """ get scores of subsector_id
    :param request: none
    :param subsector_id: specify the subsector id
    :return: scores of subsector
    """
    data = {}

    try:
        data = return_score_by_subsector(subsector_id)
        not_empty = len(data["environment"]) > 0 or len(data["social"]) > 0 or len(data["governance"]) > 0
        code = Code.GET_OK if not_empty else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(f"exception: {e}")
        print("error occurred in getting sub_sector scores")

    result = Result(code, data, success, return_message(code, "sub sector scores"))
    return JsonResponse(data=result, safe=False)


def report_notice(request, stock_code, exchange):
    """ get enterprise notice according to stock code & exchange
    :param request: none
    :param stock_code: stock code of the company
    :param exchange: exchange the company belongs to
    :return: list of notices
    """
    data = {"list": None, "total": 0}
    try:
        if exchange == "SSE":
            notices = cninfo_notice(stock_code, exchange)
            # notices = get_sse_notice(stock_code, "", 2)
        elif exchange == "SZSE":
            notices = cninfo_notice(stock_code, exchange)
        else:
            notices = get_hkse_notice(stock_code, year=10)
        data["list"] = notices
        data["total"] = len(data["list"])
        titles = []
        for n in notices:
            titles.append(n["title"])
        code = Code.GET_OK if len(data["list"]) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        print(f"exception: {e}")
        print("error occurred during fetching company notice")
        code = Code.GET_ERR
        success = False

    result = Result(code, data, success, return_message(code, "company notice"))
    return JsonResponse(data=result, safe=False)


def nlp_analysis(text_list):
    """ conducting NLP analysis to a list of sentences
    :param text_list: input sentences
    :return: a list of analysis result (i.e., 0/1)
    """
    return emotion_detection(text_list)


def fin_ratio_analysis(request, stock_code, exchange):
    """ get financial analysis result
    :param request: none
    :param stock_code: stock code of the company
    :param exchange: exchange the company belongs to
    :return: financial analysis result encapsulated in json format (i.e., {ratio1: xxx, ratio2: xxx, ...})
    """
    data = {}

    try:
        if exchange == "HKSE":
            ticker = f"{stock_code[1:]}.HK"
            data = hk_analysis(ticker=ticker)
        code = Code.GET_OK if len(data) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(f"exception: {e.with_traceback(None)}")
        print("error ")

    result = Result(code, data, success, return_message(code, "financial ratios"))
    return JsonResponse(data=result, safe=False)


def report_stock_info(request, stock_code, exchange):
    data = {"stock_info": None}

    try:
        info = stock_info_from_futu_html(stock_code, exchange)
        data["stock_info"] = info
        code = Code.GET_OK if len(data["stock_info"]) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(e)
        print("error in report stock info")

    result = Result(code, data, success, return_message(code, "stock info"))
    return JsonResponse(data=result, safe=False)


def report_stock_price(request, stock_code, exchange, interval, n):
    end = datetime.datetime.now()
    n = float(n)

    if interval == "d":
        start = end - datetime.timedelta(days=n)
    elif interval == "w":
        start = end - datetime.timedelta(days=7*n)
    else:
        start = end - datetime.timedelta(days=30*n)

    data = []

    try:
        if exchange == "HKSE":
            ticker = stock_code[1:] + ".HK"
            y_interval = "1d" if interval == "d" else ("1wk" if interval == "w" else "1mo")
            data = hk_price_from_futu(stock_code, exchange)
            if len(data) == 0:
                data = hk_stock_price(ticker, start, end, y_interval)
        elif exchange == "SZSE":
            data = sz_stock_price(stock_code)
        else:
            data = sh_stock_price(stock_code)
        code = Code.GET_OK if len(data) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(e)
        print("fetching stock price data failed")

    result = Result(code, data, success, return_message(code, "stock price data"))
    return JsonResponse(data=result, safe=False)


def report_stock_sector(request, stock_code, exchange):
    data = {}

    try:
        data = get_sector(stock_code, exchange)
        code = Code.GET_OK if len(data) > 0 else Code.GET_OK_BUT_EMPTY
        success = True
    except Exception as e:
        code = Code.GET_ERR
        success = False
        print(e)

    print(data)

    result = Result(code, data, success, return_message(code, "msci data"))
    return JsonResponse(data=result, safe=False)


def news(request):
    return render(request, "companies/news.html")


def industry(request):
    return render(request, "companies/industry.html")


def about_us(request):
    return render(request, "companies/about-us.html")


def report(request):
    try:
        company = dict(request.GET)
        name = company["name"][0]
        stock_code = company["code"][0]
        exchange = company["market"][0]
        enterprise = {"name": name, "code": stock_code, "market": exchange}
        print(enterprise)
        return render(request, "companies/report.html", {"company": json.dumps(enterprise)})
    except Exception as e:
        return render(request, "companies/index.html")
