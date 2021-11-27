# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import pandas as pd
from datetime import date
from datetime import timedelta
import datetime
from pymongo import MongoClient

mongoclient = "mongodb://127.0.0.1:27017"
database = "nse"
options_collection = "options_chain"
cash_collection = "cash_market"
dump_52wk = "dump_52wk"

client = MongoClient(mongoclient)
db = client[database]

dump_to_db = db[dump_52wk]

dump_to_db.delete_many({})
