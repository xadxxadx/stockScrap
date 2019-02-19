import datetime
import requests
import pandas as pd
from io import StringIO
from io import BytesIO
import os
import re
import numpy as np
import time

twse_request_format = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALL'
tpex_request_format = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_download.php?l=zh-tw&d={}&s=0,asc,0'
csv_path = 'stocks_csv/'

def get_twse_by_date(date):
    dateStr = date.strftime("%Y%m%d")
    filePath = csv_path + 'twse/' + dateStr + '.csv'
    if not os.path.isfile(filePath):
        r = requests.post(twse_request_format.format(dateStr))

        if not os.path.exists(csv_path):
            os.mkdir(csv_path)

        twse_path = csv_path + 'twse/'
        if not os.path.exists(twse_path):
            os.mkdir(twse_path)

        if not r.text:
            zero_data = np.zeros(shape=[1, 3])
            d = pd.DataFrame(zero_data)
            open(twse_path + dateStr + '.csv', 'a').close()
            return d
        df = pd.read_csv(StringIO('\n'.join(n for n in r.text.split('\n') if len(n.split('",')) == 17 and n[0] != '=')))


        df.to_csv(twse_path + dateStr + '.csv', encoding='utf_8_sig')
    else:
        try:
            df = pd.read_csv(filePath, encoding='utf_8_sig')
        except:
            df = pd.DataFrame(np.zeros(shape=[1, 3]))
    return df


def get_tpex_by_date(date):
    fileDateStr = date.strftime("%Y%m%d")
    filePath = csv_path + 'tpex/' + fileDateStr + '.csv'
    if not os.path.isfile(filePath):
        requestDateStr = '{}/{}/{}'.format(str(date.year - 1911).zfill(3), str(date.month).zfill(2), str(date.day).zfill(2))
        r = requests.post(tpex_request_format.format(requestDateStr))
        if not os.path.exists(csv_path):
            os.mkdir(csv_path)

        tpex_path = csv_path + 'tpex/'
        if not os.path.exists(tpex_path):
            os.mkdir(tpex_path)

        if not r.text:
            zero_data = np.zeros(shape=[1, 3])
            d = pd.DataFrame(zero_data)
            open(filePath, 'a').close()
            return d
        r.encoding = 'big5hkscs'
        #df = pd.read_csv(StringIO('\n'.join(n for n in r.text.split('\n') if (len(n.split('",')) == 17 or len(n.split(' ,')) == 17) and '購' not in n and '售' not in n)))
        df = pd.read_csv(StringIO('\n'.join(n for n in r.text.split('\n') if
                    len(re.findall('\D,', n)) == 16 and '購' not in n and '售' not in n)))

        df.to_csv(filePath, encoding='utf_8_sig')
    else:
        try:
            df = pd.read_csv(filePath, encoding='utf_8_sig')
        except:
            df = pd.DataFrame(np.zeros(shape=[1, 3]))
    return df


def get_trade_info(stockID, date):
    df = get_twse_by_date(date)
    idCol = df.iloc[:, 1:3]
    index = np.where(idCol == stockID)
    if not index[0]:
        df = get_tpex_by_date(date)
        idCol = df.iloc[:, 1:3]
        index = np.where(idCol == stockID)

    if index[0]:
        return df.iloc[index[0][0], :]
    else:
        zero_data = np.zeros(shape=[0, 0])
        d = pd.DataFrame(zero_data)
        return d


def get_trade_section_info(stockID, dateFrom, dateTo):
    dayCount = (dateTo - dateFrom).days + 1
    stockDatas = []
    for single_date in (dateFrom + datetime.timedelta(n) for n in range(dayCount)):
        while True:
            try:
                stockData = get_trade_info(stockID, single_date)
                if not stockData.empty:
                    stockDatas.append((pd.Series(single_date.strftime("%Y%m%d")), stockData))
                break
            except:
                print('Get Info Exception, Sleep 60s, {}'.format(single_date))
                time.sleep(60)
        print(single_date)

    #stockDatas = [(pd.Series(single_date.strftime("%Y%m%d")), get_trade_info(stockID, single_date))
     #        for single_date in (dateFrom + datetime.timedelta(n) for n in range(dayCount))]
    stockDatas = [pd.concat([pd.Series(dateKey), valFrame.iloc[1:]]) for dateKey, valFrame in stockDatas if not valFrame.empty]
    if len(stockDatas) == 0:
        return pd.DataFrame.empty
    stockDatas = pd.concat(stockDatas, axis=1)
    return stockDatas.T
    #frame = [pd.concat([pd.Series(single_date.strftime("%Y%m%d")), get_trade_info(stockID, single_date).iloc[1:]])
      #       for single_date in (dateFrom + datetime.timedelta(n) for n in range(dayCount))]
    #frame = pd.concat(frame, axis=1)

