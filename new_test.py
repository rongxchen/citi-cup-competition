# obtaining data
#import requests
# import json
#
# from web_crawler.utils import get_random_ua
#
# url = "https://api.nasdaq.com/api/company/SBUX/financials?frequency=1"
# headers = {
#     "user-agent": get_random_ua(),
#     "origin": "https://www.nasdaq.com",
#     "referer": "https://www.nasdaq.com/",
# }
# resp = requests.get(url=url, headers=headers)
#
# with open("sbux.json", "w") as file:
#     file.write(json.dumps(resp.json()))


# processing data
import json
import pandas as pd

pd.set_option("display.max_columns", None)

def clean_data(data: dict):
    table = {}
    values = {}

    for header in data["headers"]:
        table[data["headers"][header]] = []
        values[header] = data["headers"][header]

    for row in range(len(data["rows"])):
        row_data = data["rows"][row]
        for v in row_data:
            if row_data[v] == "--":
                table[values[v]].append("--")
                continue
            if row_data[v].startswith("$") or row_data[v].startswith("-"):
                row_data[v] = float(row_data[v].replace("$", "").replace(",", ""))
            table[values[v]].append(row_data[v])
    rebuilt_table = pd.DataFrame(table)
    return rebuilt_table


with open("sbux.json", "r") as file:
    sbux = json.loads(file.read())["data"]
    balance_sheet = clean_data(sbux["balanceSheetTable"])
    income_statement = clean_data(sbux["incomeStatementTable"])

balance_sheet.to_excel("sbux_balance_sheet.xlsx")
income_statement.to_excel("sbux_income_statement.xlsx")


# read data
# import pandas as pd
#
# pd.set_option("display.max_columns", None)
#
# balance_sheet = pd.read_excel("sbux_balance_sheet.xlsx").drop(columns="Unnamed: 0")
# print(balance_sheet)
