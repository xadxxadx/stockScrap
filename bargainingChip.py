import datetime
import requests

url_financing = 'http://jsjustweb.jihsun.com.tw/z/zc/zcn/zcn.djhtm?a={}&c={}&d={}'
path_stock =  'stocks_data/'

def get_financing(stockID, dateFrom, dateTo):
    datefromStr = dateFrom.strftime("%Y-%m-%d")
    dateToStr = dateTo.strftime("%Y-%m-%d")
    r = requests.get(url_financing.format(stockID, datefromStr, dateToStr))
    print(r.text)