# -*- coding: utf-8 -*-

import pandas as pd
from datetime import date
from datetime import timedelta
import datetime
from pymongo import MongoClient
import urllib

mongoclient = (
    "mongodb+srv://happyadmin:"
    + urllib.parse.quote_plus("Happy@123")
    + "@cluster0.eyb8f.mongodb.net/happyinvesting?retryWrites=true&w=majority"
)
database = "happyinvesting"
options_collection = "options_chain"
cash_collection = "cash_market"
dump_52wk = "dump_52wk"
# symbol="TCS"

df = pd.read_csv("stock_symbols.csv")
all_stock_codes = df.Symbol.tolist()

end_date = datetime.datetime.today()
start_date = end_date - timedelta(weeks=52)

start_date10 = end_date - timedelta(weeks=10)
start_date1M = end_date - timedelta(weeks=7)


client = MongoClient(mongoclient)
db = client[database]


for symbol in all_stock_codes:
    try:
        dump = pd.DataFrame(
            list(
                db[cash_collection].find(
                    {
                        "TIMESTAMP": {"$gte": start_date, "$lte": end_date},
                        "SYMBOL": symbol,
                    }
                )
            )
        )
        dump10 = pd.DataFrame(
            list(
                db[cash_collection].find(
                    {
                        "TIMESTAMP": {"$gte": start_date10, "$lte": end_date},
                        "SYMBOL": symbol,
                    }
                )
            )
        )
        dump1M = pd.DataFrame(
            list(
                db[cash_collection].find(
                    {
                        "TIMESTAMP": {"$gte": start_date1M, "$lte": end_date},
                        "SYMBOL": symbol,
                    }
                )
            )
        )

        data = {
            "SYMBOL": symbol,
            "52WKH": dump["HIGH"].max(),
            "52WKL": dump["LOW"].min(),
            "1MV": dump["TOTTRDQTY"].mean(),
        }
        try:
            data["10DH"] = dump10["HIGH"].max()
            data["10DL"] = dump10["LOW"].min()
        except:
            data["10DH"] = 0
            data["10DL"] = 0

        dump_to_db = db[dump_52wk]

        print(data)

        # insert into dump database
        dump_to_db.insert(data)
    except:
        print("No data for " + symbol)


# calculate max high and min high from the dump

# max_high = db.dump_52wk.find_one(sort=[("HIGH", -1)])
# max_high = max_high["HIGH"]

# min_high = db.dump_52wk.find_one(sort=[("HIGH", 1)])
# min_high = min_high["HIGH"]
