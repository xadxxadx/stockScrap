import datetime
import requests
import pandas as pd
from io import StringIO
from io import BytesIO
import os
import re
import numpy as np
import time
import json


twse_request_format = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'
tpex_request_format = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'
csv_path = 'stocks_csv_Json/'

def get_twse_by_date(date):
    dateStr = date.strftime("%Y%m%d")
    filePath = csv_path + 'twse/' + dateStr + '.json'
    if not os.path.isfile(filePath):
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'
        query_params = {
            'date': dateStr,
            'response': 'json',
            'type': 'ALL',
            '_': str(round(time.time() * 1000) - 500)
        }
        page = requests.get(url, params=query_params)
        if not page.ok:
            print("Can not get TSE data at {}".format(dateStr))
            return##to do
        content = page.json()
        if 'data5' not in content:
            result = {}
        else:
            result = content['data5']

        if not os.path.exists(csv_path):
            os.mkdir(csv_path)

        twse_path = csv_path + 'twse/'
        if not os.path.exists(twse_path):
            os.mkdir(twse_path)

        with open(filePath, 'w', encoding='utf_8_sig') as outfile:
            json.dump(result, outfile)
    else:
        with open(filePath, 'r', encoding='utf_8_sig') as outfile:
            result = json.load(outfile)
    return result


def get_tpex_by_date(date):
    fileDateStr = date.strftime("%Y%m%d")
    filePath = csv_path + 'tpex/' + fileDateStr + '.json'
    if not os.path.isfile(filePath):
        requestDateStr = '{}/{}/{}'.format(str(date.year - 1911).zfill(3), str(date.month).zfill(2),str(date.day).zfill(2))
        url = tpex_request_format.format(requestDateStr, str(int(time.time() * 100)))

        page = requests.post(url)
        page.encoding = 'big5hkscs'
        content = page.json()

        if not os.path.exists(csv_path):
            os.mkdir(csv_path)

        tpex_path = csv_path + 'tpex/'
        if not os.path.exists(tpex_path):
            os.mkdir(tpex_path)

        result = content['mmData']
        result.extend(content['aaData'])

        with open(filePath, 'w', encoding='utf_8') as outfile:
            json.dump(result, outfile)
    else:
        with open(filePath, 'r', encoding='utf_8') as outfile:
            result = json.load(outfile)
    #df = pd.DataFrame(content['aaData'])

    return result


def get_recently_valid_date():
    date = datetime.datetime.now() - datetime.timedelta(days=1)
    while not get_twse_by_date(date) and not  get_tpex_by_date(date):
        date = date - datetime.timedelta(days=1)
    return date


def get_stock_name_match(stockID, date = get_recently_valid_date()):
    twseJs = get_twse_by_date(date)
    twseJsNameID = pd.DataFrame([n[0:2] for n in twseJs])
    index = np.where(twseJsNameID == stockID)

    if index[0]:
        return twseJsNameID.iloc[index[0][0], 0]

    tpexJs = get_tpex_by_date(date)
    tpexJsNameID = pd.DataFrame([n[0:2] for n in tpexJs])
    index = np.where(tpexJsNameID == stockID)

    if index[0]:
        return tpexJsNameID.iloc[index[0][0], 0]
    return ''


def get_trade_info(stockID, date, checkID = False):
    '''format = #ID,Name,開,高,低,收,股,筆,金 '''
    if checkID and not get_stock_name_match(stockID, date=date):
        return []

    data = get_twse_by_date(date)
    index = [i for i, elem in enumerate(data) if elem[0]==stockID]
    if index:
        element = data[index[0]]
        return element[0:2] + element[5:9] + element[2:5]

    data = get_tpex_by_date(date)
    index = [i for i, elem in enumerate(data) if elem[0] == stockID]
    if index:
        element = data[index[0]]
        return element[0:2] + element[4:7] + [element[2] , element[8] , element[10] , element[9]]
    return []


def get_trade_section_info(stockID, dateFrom, dateTo):
    dayCount = (dateTo - dateFrom).days + 1
    stockDatas = []
    for single_date in (dateFrom + datetime.timedelta(n) for n in range(dayCount)):
        while True:
            try:
                stockData = get_trade_info(stockID, single_date, checkID=False)
                if stockData:
                    stockDatas.append([single_date.strftime("%Y%m%d")] + stockData)
                break
            except:
                print('Get Info Exception, Sleep 60s, {}'.format(single_date))
                time.sleep(60)
        print(single_date)
        time.sleep(10)
    if len(stockDatas) == 0:
        return pd.DataFrame.empty
    else:
        return pd.DataFrame(stockDatas)


