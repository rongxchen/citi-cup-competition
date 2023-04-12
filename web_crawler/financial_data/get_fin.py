import yahooquery as yq
import pandas as pd
import math

pd.set_option("display.max_columns", None)


def hk_analysis(ticker):
    """ calculate and return the financial analysis data
    :param ticker: special sticker for HK stock market when using yahoo query
    :return: result encapsulated in json format
    """
    t = yq.Ticker(ticker)
    income_statement = t.income_statement(frequency="a", trailing=False)
    balance_sheet = t.balance_sheet(frequency="a", trailing=False)

    # index of -1 is to get the latest year data
    net_income = income_statement["NetIncome"][-1]
    pFY_net_income = income_statement["NetIncome"][-2]
    ppFY_net_income = income_statement["NetIncome"][-3]
    EBITDA = income_statement["NormalizedEBITDA"][-1]
    total_asset = balance_sheet["TotalAssets"][-1]
    pFY_total_asset = balance_sheet["TotalAssets"][-2]
    tax_expenses = income_statement["TaxProvision"][-1]
    interest_expense = income_statement["InterestExpense"][-1]
    total_shareholer_equity = balance_sheet["TotalEquityGrossMinorityInterest"][-1]
    pFY_total_shareholer_equity = balance_sheet["TotalEquityGrossMinorityInterest"][-2]
    current_asset = balance_sheet["CurrentAssets"][-1]
    current_liability = balance_sheet["CurrentLiabilities"][-1]
    try:
        inventory = balance_sheet["Inventory"][-1]
    except Exception as e:
        inventory = 0
    prepaid_assets = balance_sheet["PrepaidAssets"][-1]
    total_revenue = income_statement["TotalRevenue"][-1]
    total_assets = balance_sheet["TotalAssets"][-1]

    # 利润总额
    total_income = EBITDA
    # 净利润
    net_income = net_income
    # 平均asset
    avg_asset = (pFY_total_asset + total_asset) * 0.5
    # 平均shareholder equity
    avg_shareholder_equity = (total_shareholer_equity + pFY_total_shareholer_equity) * 0.5
    # 净利润三年平均增长
    gr_2021 = (net_income - pFY_net_income) / pFY_net_income
    gr_2020 = (pFY_net_income - ppFY_net_income) / ppFY_net_income
    grouth_rate_net_income = math.sqrt((gr_2021 + 1) * (gr_2020 + 1)) - 1
    # 流动比率
    lr = current_asset / current_liability
    # 速动比率
    qr = (current_asset - prepaid_assets - inventory) / current_liability
    # 资产周转率
    assets_turnover = total_revenue / total_assets
    # 总资产对数值
    lnassets = math.log(total_assets)

    return_on_asset = (total_income / avg_asset) * 100
    return_on_equity = (net_income / avg_asset) * 100
    liquid_ratio = lr
    quick_ratio = qr
    net_benefit_3y = grouth_rate_net_income * 100
    log_asset = lnassets

    ratios = {
        "return_on_asset": round(return_on_asset, 4),
        "return_on_equity": round(return_on_equity, 4),
        "liquid_ratio": round(liquid_ratio, 4),
        "quick_ratio": round(quick_ratio, 4),
        "net_benefit_3y": round(net_benefit_3y, 4),
        "asset_turnover": round(assets_turnover, 4),
        "log_asset": round(log_asset, 4),
    }

    return ratios
