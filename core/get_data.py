from pandas_datareader import data as pdr
import pandas as pd
import json, os
from django.conf import settings
from nsetools import Nse
import yfinance as yf


def getData():
    df = pd.read_csv(os.path.join(settings.BASE_DIR, "core", "stock_symbols.csv"))
    all_stock_codes = df.Symbol.tolist()
    all_tickers = [x + ".NS" for x in all_stock_codes[0:5]]
    all_tickers = ",".join([elem for elem in all_tickers])
    yf.pdr_override()
    data = 0
    data = pdr.get_data_yahoo(
        tickers=all_tickers,
        period="1d",
        interval="1d",
        group_by="ticker",
        threads=False,
    )
    print(data)
    data.reset_index(drop=True, inplace=True)
    try:
        data = data.drop(1)
    except:
        pass
    data = data.stack()
    reset_df = data.reset_index()
    reset_df = reset_df.set_index("level_1")
    reset_df = reset_df.drop("level_0", axis=1)
    data = reset_df
    print(data)
    # data.set_index("Date")
    res = data.to_json(orient="columns", double_precision=2)
    print(res)
    res = json.loads(res)
    res_without_NS = dict()
    for key, value in res.items():
        t = key.split(".")
        res_without_NS[t[0]] = value
    return res_without_NS
