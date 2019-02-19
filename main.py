import  datetime
import  stockScrap
import os
import time
import requests
import re
import stockScrapJ
import bargainingChip


def main():
    #df1 = stockScrap.get_trade_info('5291', datetime.datetime(2019,1,25))
    #df = stockScrap.get_trade_section_info('9487123', datetime.datetime(2015,1,1), datetime.datetime(2019,1,28))
    #print(df)
    #variables = {'korea'}
    #exec(compile(open("vpngate.py", "rb").read(), "vpngate.py", 'exec'), variables, locals)
    #print(stockScrapJ.get_stock_name_match('10628'))
    #print(stockScrapJ.get_trade_info('6150', datetime.datetime(2019,1,28)))
    #print(stockScrapJ.get_tpex_by_date(datetime.datetime(2019,1,26)))
    df = stockScrapJ.get_trade_section_info('6150', datetime.datetime(2010, 1, 1), datetime.datetime(2019, 1, 1))
    #bargainingChip.get_financing('6150', datetime.datetime(2015, 1, 1), datetime.datetime(2019, 1, 1))
if __name__ == '__main__':
    main()