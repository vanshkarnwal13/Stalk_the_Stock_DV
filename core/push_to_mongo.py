from pymongo import MongoClient
import urllib 
import pandas as pd

def dataPreparationCash(code, data, sectors):
    # data['EXPIRY_DT'] = pd.to_datetime(data['EXPIRY_DT'])
    # data = data[data["SYMBOL"]==code]
    data = pd.merge(data,sectors,on = "SYMBOL",how="left")   
    data = data.drop(["Series","ISIN Code","Industry.1"],axis = 1)
    data = data.rename(columns = {"Company Name":"COMPANY_NAME","Industry":"SECTOR"})
    data = data.fillna(0)
    data = data.to_dict('records')
    return data

#function for inserting the data inside mongodb
def insertintoMongo(database,collection,data):
    client =MongoClient("mongodb://localhost:27017/")
    db = client[database]
    options_chain = db[collection]
    options_chain.insert_many(data)

# print(data)
# data = dataPreparationCash("TATASTEEL")

df = pd.read_csv("stock_symbols.csv")

all_stock_codes = df.Symbol.tolist()
data = pd.read_csv("cash_market.csv")
cols = ["Unnamed: 13","Unnamed: 11"] #unwanted columns
# data = data[data['SERIES'] == "EQ"] 
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])

sectors = pd.read_csv("StocksandSector.csv")    
sectors = sectors.rename(columns = {"Symbol":"SYMBOL"})
dat = dataPreparationCash("NIFTY 50", data, sectors)
print(dat)
insertintoMongo( "happyinvesting", "cash_market", dat)

# for i in cols:
#     if i in data.columns:
#         data = data.drop([i],axis = 1)
# for code in all_stock_codes:
#     print(code) 
#     try:
#         dat = dataPreparationCash(code, data, sectors)
#         insertintoMongo( "happyinvesting", "options_chain", dat)
#     except:
#         print("Error in inserting data for ",code)

"""
ADANIPORTS
AXISBANK
BAJFINANCE
BHARTIARTL
HINDALCO
IOC
ONGC
MARUTI
INDUSINDBK
SBIN
SUNPHARMA
TATAMOTORS
TATASTEEL
ULTRACEMCO
data = investpy.get_index_historical_data(index='NIFTY 50', country='india', from_date='08/08/2021', to_date='09/08/2021')
"""
