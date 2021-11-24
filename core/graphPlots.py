import pandas as pd
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from pymongo import MongoClient
from pandas_datareader import data as pdr
import datetime
import calendar
import urllib


def get_client():
    return MongoClient(
        "mongodb+srv://happyadmin:"
        + urllib.parse.quote_plus("Happy@123")
        + "@cluster0.eyb8f.mongodb.net/happyinvesting?retryWrites=true&w=majority&authSource=admin"
    )


def load_data_realtime(collection, symbol):
    print("inside load_data 52week....")
    # load data from csv
    data = pd.read_csv("data/dump_52wk.csv")
    # filter data with symbol
    data = data[data["SYMBOL"] == symbol]
    # data = pd.DataFrame(list(db["dump_52wk"].find({"SYMBOL": symbol})))
    return data


def load_data(collection, symbol, today, yesterday):
    print("inside load_data....")
    today = datetime.datetime(today.year, today.month, today.day)
    yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
    # client = get_client()
    # db = client["happyinvesting"]
    data = pd.read_csv("data/cash_market.csv", index_col=False)
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    data = data[
        (data["TIMESTAMP"] >= str(yesterday))
        & (data["TIMESTAMP"] <= str(today))
        & (data["SYMBOL"] == symbol)
    ]
    return data


def load_sector_data(collection, today, yesterday):
    print("inside load_data sector....")
    today = datetime.datetime(today.year, today.month, today.day)
    yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
    # client = get_client()
    # db = client["happyinvesting"]

    data = pd.read_csv("data/cash_market.csv", index_col=False)
    # for time in data["TIMESTAMP"]:
    #     time = datetime.datetime.fromisoformat(time[:-1])
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    data = data[
        (data["TIMESTAMP"] >= str(yesterday)) & (data["TIMESTAMP"] <= str(today))
    ]
    return data


# function to get weeknames in a day
def Get_weeknames(Share_Data):
    list_v = []
    for d in Share_Data["TIMESTAMP"]:
        Share_Data["TIMESTAMP"] = pd.to_datetime(Share_Data["TIMESTAMP"])
        if d.weekday() == 0:
            list_v.append("Monday")
        elif d.weekday() == 1:
            list_v.append("Tuesday")
        elif d.weekday() == 2:
            list_v.append("Wednesday")
        elif d.weekday() == 3:
            list_v.append("Thursday")
        elif d.weekday() == 4:
            list_v.append("Friday")
        elif d.weekday() == 5:
            list_v.append("Saturday")
        else:
            list_v.append("Sunday")
    return list_v


# function to get week number of date
def Get_week_num(Share_Data):
    Week = []
    for d in Share_Data["TIMESTAMP"]:
        Week.append(d.week)
    return Week


# function to get Quarter of a month
def Get_Quarter_num(Share_Data):
    Quarter = []
    for d in Share_Data["TIMESTAMP"]:
        if d in range(1, 5):
            Quarter.append("First")
        elif d in range(5, 9):
            Quarter.append("Second")
        else:
            Quarter.append("Third")
    return Quarter


def get_previous_open(data):
    Open_Value = [1]
    for open_value in data["OPEN"]:
        Open_Value.append(open_value)
    Open_Value.pop()
    return Open_Value


def get_nifty(collection):
    client = get_client()
    db = client["happyinvesting"]
    nifty = pd.DataFrame(list(db[collection].find({"SYMBOL": "NIFTY 50"})))
    nifty = nifty.loc[:, ["CLOSE", "TIMESTAMP"]]
    nifty = nifty.rename(columns={"CLOSE": "NIFTY"})
    nifty = nifty.sort_values(by="TIMESTAMP")
    return nifty


def Get_previous_close(Share_Data):
    Close_Value = [1]
    for Value in Share_Data["CLOSE"]:
        Close_Value.append(Value)
    Close_Value.pop()
    return Close_Value


# function to get continous percentage change in closing price
def Continous_change_close(Share_Data):
    Per_close = []
    for d in Share_Data["Percent_Change_close"]:
        if d > 0:
            Per_close.append(1)
        else:
            Per_close.append(0)
    return Per_close


# function to get continous percentage change in opening price
def Continous_change_open(Share_Data):
    Per_open = []
    for d in Share_Data["Percent_Change_open"]:
        if d > 0:
            Per_open.append(1)
        else:
            Per_open.append(0)
    return Per_open


# function to get continous percentage change in day price
def Continous_change_day(Share_Data):
    Per_day = []
    for d in Share_Data["Percent_Change_day"]:
        if d > 0:
            Per_day.append(1)
        else:
            Per_day.append(0)
    return Per_day


# function to check wheather High > close value in a stock
def High_close_day(Share_Data):
    High_close = []
    for i, j in zip(Share_Data["HIGH"], Share_Data["CLOSE"]):
        if i > j:
            High_close.append(1)
        else:
            High_close.append(0)
    return High_close


# function to check wheather low < close value in a stock
def Low_close_day(Share_Data):
    Low_close = []
    for i, j in zip(Share_Data["LOW"], Share_Data["CLOSE"]):
        if i < j:
            Low_close.append(1)
        else:
            Low_close.append(0)
    return Low_close


# function to check wheather High > open value in a stock
def High_open_day(Share_Data):
    High_open = []
    for i, j in zip(Share_Data["HIGH"], Share_Data["OPEN"]):
        if i > j:
            High_open.append(1)
        else:
            High_open.append(0)
    return High_open


# function to check wheather low < open value in a stock
def Low_open_day(Share_Data):
    Low_open = []
    for i, j in zip(Share_Data["LOW"], Share_Data["OPEN"]):
        if i < j:
            Low_open.append(1)
        else:
            Low_open.append(0)
    return Low_open


# function to get year on year data
def yearly_data(Share_Data):
    Table_Year = []
    for j in Share_Data["TIMESTAMP"].dt.year.unique():
        yearly_close = []
        yearly_close.append(j)
        include = Share_Data[Share_Data["TIMESTAMP"].dt.year == j]
        Min_Value = (
            include["CLOSE"]
            .loc[(include["TIMESTAMP"] == include["TIMESTAMP"].min())]
            .reset_index()
            .iloc[0]["CLOSE"]
        )
        Max_Value = (
            include["CLOSE"]
            .loc[(include["TIMESTAMP"] == include["TIMESTAMP"].max())]
            .reset_index()
            .iloc[0]["CLOSE"]
        )
        yearly_close.append(((Max_Value - Min_Value) / Min_Value) * 100)
        Table_Year.append(yearly_close)
    Close_Year_Table = pd.DataFrame(
        Table_Year, columns=["Year", "%Change_Closing_Price"]
    )
    return Close_Year_Table


def monthly_data(Share_Data):
    Table_Month = []
    for j in Share_Data["TIMESTAMP"].dt.year.unique():
        include = Share_Data[Share_Data["TIMESTAMP"].dt.year == j]
        for months in include["TIMESTAMP"].dt.month.unique():
            Monthly_close = []
            Monthly_close.append(j)
            Monthly_close.append(months)
            include_month = include[include["TIMESTAMP"].dt.month == months]
            Min_Value = (
                include_month["CLOSE"]
                .loc[(include_month["TIMESTAMP"] == include_month["TIMESTAMP"].min())]
                .reset_index()
                .iloc[0]["CLOSE"]
            )
            Max_Value = (
                include_month["CLOSE"]
                .loc[(include_month["TIMESTAMP"] == include_month["TIMESTAMP"].max())]
                .reset_index()
                .iloc[0]["CLOSE"]
            )
            Monthly_close.append(((Max_Value - Min_Value) / Min_Value) * 100)
            Table_Month.append(Monthly_close)
    Close_Month_Table = pd.DataFrame(
        Table_Month, columns=["Year", "Months", "%Change_Closing_Price"]
    )
    Close_Month_Table["Months"] = Close_Month_Table["Months"].apply(
        lambda x: calendar.month_abbr[x]
    )
    return Close_Month_Table


# fuction to display the probablity table for weekdays based on years
def Probability_Table(Share_Data):
    Table = []
    for j in Share_Data["TIMESTAMP"].dt.year.unique():
        Include_Year = Share_Data[Share_Data["TIMESTAMP"].dt.year == j]
        Per_year = []
        Per_year.append(j)
        for days in Include_Year["Day"].unique():
            if days not in ["Saturday", "Sunday"]:
                Prob_high = Include_Year[
                    (Include_Year["Day"] == days)
                    & (Include_Year["TIMESTAMP"].dt.year == j)
                    & (Include_Year["Continuous_%change_close"] > 0)
                ]
                Prob_low = Include_Year[
                    (Include_Year["Day"] == days)
                    & (Include_Year["TIMESTAMP"].dt.year == j)
                    & (Include_Year["Continuous_%change_close"] < 1)
                ]
                Prob_value = Prob_high.shape[0] / (
                    Prob_high.shape[0] + Prob_low.shape[0]
                )
                Per_year.append(Prob_value)
        Table.append(Per_year)
    Prob_Table = pd.DataFrame(
        Table, columns=["Year", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    return Prob_Table


def Cash_process_data(start_date, end_date, symbol, cash_collection):
    start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
    data = load_data(cash_collection, symbol, end_date, start_date)
    data = data.sort_values("TIMESTAMP")
    if "PREVCLOSE" not in data:
        data["PREVCLOSE"] = Get_previous_close(data)
    else:
        pass
    data["PREVOPEN"] = get_previous_open(data)
    data["Percent_Change_close"] = (
        (data["CLOSE"] - data["PREVCLOSE"]) / data["PREVCLOSE"]
    ) * 100
    data["Percent_Change_open"] = (
        (data["OPEN"] - data["PREVOPEN"]) / data["PREVOPEN"]
    ) * 100
    data["Percent_Change_day"] = ((data["CLOSE"] - data["OPEN"]) / data["OPEN"]) * 100
    data["Day"] = Get_weeknames(data)
    data["Month"] = data["TIMESTAMP"].dt.month
    data["Quarter"] = Get_Quarter_num(data)
    data["Week"] = Get_week_num(data)
    data["Continuous_%change_close"] = Continous_change_close(data)
    data["Continuous_%change_open"] = Continous_change_open(data)
    data["Continuous_%change_day"] = Continous_change_day(data)
    data["Day's High>Close"] = High_close_day(data)
    data["Day's Low<Close"] = Low_close_day(data)
    data["Day's High>Open"] = High_open_day(data)
    data["Day's Low<Open"] = Low_open_day(data)
    return data


def corr_with_nifty(collection, nifty, symbol):
    client = get_client()
    db = client["happyinvesting"]
    data = pd.DataFrame(list(db[collection].find({"SYMBOL": symbol})))
    data = data.loc[:, ["CLOSE", "TIMESTAMP"]]
    data = data.rename(columns={"CLOSE": symbol})
    data = data.sort_values(by="TIMESTAMP")
    corr_data = pd.DataFrame()
    corr_data = pd.merge(nifty, data, how="inner", on="TIMESTAMP")
    corr_data = corr_data.drop(["TIMESTAMP"], axis=1)
    return corr_data


def df_to_plotly(df):
    return {"z": df.values.tolist(), "x": df.columns.tolist(), "y": df.index.tolist()}


def generate_analysis1(ticker):
    end_date = datetime.datetime.today()
    start_date = datetime.datetime.now() - datetime.timedelta(days=5 * 365)
    symbol = ticker
    data = Cash_process_data(start_date, end_date, symbol, "cash_market")

    start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
    # data = load_data("cash_market",symbol,end_date,start_date)
    # data = data[data['SYMBOL']=="20MICRONS"]
    plotly_figure1 = px.line(
        data_frame=data, x=data["TIMESTAMP"], y=data["CLOSE"], height=400
    )
    plotly_figure1.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure1.update_layout(
        title="Close Price Chart",
        xaxis_title="Time Period",
        yaxis_title="Close Price",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    " " "### Open price of share" " "
    plotly_figure2 = px.line(
        data_frame=data, x=data["TIMESTAMP"], y=data["OPEN"], height=400
    )
    plotly_figure2.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure2.update_layout(
        title="Open Price Data",
        xaxis_title="Time Period",
        yaxis_title="Open Price",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    " " "### Percentage of change in Closing price of share" " "
    plotly_figure3 = px.histogram(
        data_frame=data, x=data["Percent_Change_close"], height=400
    )
    plotly_figure3.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure3.update_layout(
        title="% Change Close",
        xaxis_title="Time Period",
        yaxis_title="% Change",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    " " "### Percentage of change in Opening price of share" " "
    plotly_figure4 = px.histogram(
        data_frame=data, x=data["Percent_Change_open"], height=400
    )
    plotly_figure4.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure4.update_layout(
        title="% Change Open",
        xaxis_title="Time Period",
        yaxis_title="% Change",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    " " "### Percentage of change in Opening and close price of share" " "
    plotly_figure5 = px.histogram(
        data_frame=data, x=data["Percent_Change_day"], height=400
    )
    plotly_figure5.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure5.update_layout(
        title="% Change Daily (Chaal)",
        xaxis_title="% Change Span",
        yaxis_title="No of Times/Frequency",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    nifty = get_nifty("cash_market")
    corr_data = corr_with_nifty("cash_market", nifty, symbol)
    corr_fig1 = px.imshow(
        corr_data.corr(),
        labels={"color": "Correlation"},
        zmin=-1,
        zmax=1,
        color_continuous_scale="Inferno",
        height=400,
    )
    corr_fig1.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    corr_fig1.update_layout(
        title="Nifty & Share Relations",
        xaxis_title="Nifty",
        yaxis_title="Share",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    plotly_figure6 = px.line(
        data, x="TIMESTAMP", y="Continuous_%change_close", height=400
    )
    plotly_figure6.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure6.update_layout(
        title="Continuous_%change_close",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    Probability_df = Probability_Table(data)
    plotly_figure7 = go.Figure(
        data=go.Heatmap(df_to_plotly(Probability_df.set_index("Year")))
    )
    # plotly_figure7=px.line(data,x ="TIMESTAMP",y="Continuous_%change_close")
    plotly_figure7.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure7.update_layout(
        title="Plot Title",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    Yearly_df = yearly_data(data)
    plotly_figure8 = px.line(data_frame=Yearly_df, x="Year", y="%Change_Closing_Price")
    plotly_figure8.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    plotly_figure8.update_layout(
        title="%Change_Closing_Price Yearly",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    monthly_df = monthly_data(data)
    final_years = monthly_df[["Year", "Months", "%Change_Closing_Price"]]
    pivot_table = final_years.pivot(
        index="Year", columns="Months", values="%Change_Closing_Price"
    )
    fig = go.Figure(data=go.Heatmap(df_to_plotly(pivot_table), colorscale="Viridis"))
    fig.update_layout(
        height=300,
        font=dict(size=10),
        xaxis=dict(tickmode="linear"),
        yaxis=dict(tickmode="linear"),
    )
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    fig.update_layout(
        title="%Change_Closing_Price- Monthly",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    return (
        plotly_figure1,
        plotly_figure2,
        plotly_figure3,
        plotly_figure4,
        plotly_figure5,
        plotly_figure6,
        plotly_figure7,
        plotly_figure8,
        corr_fig1,
        fig,
    )


def sector_yearly_data(Share_Data, symbol):
    Table_Year = []
    for j in Share_Data["TIMESTAMP"].dt.year.unique():
        yearly_close = []
        yearly_close.append(j)
        yearly_close.append(symbol)
        include = Share_Data[Share_Data["TIMESTAMP"].dt.year == j]
        Min_Value = (
            include["CLOSE"]
            .loc[(include["TIMESTAMP"] == include["TIMESTAMP"].min())]
            .reset_index()
            .iloc[0]["CLOSE"]
        )
        Max_Value = (
            include["CLOSE"]
            .loc[(include["TIMESTAMP"] == include["TIMESTAMP"].max())]
            .reset_index()
            .iloc[0]["CLOSE"]
        )
        yearly_close.append(((Max_Value - Min_Value) / Min_Value) * 100)
        Table_Year.append(yearly_close)
    Close_Year_Table = pd.DataFrame(
        Table_Year, columns=["Year", "Symbol", "%Change_Closing_Price"]
    )
    return Close_Year_Table


def sector_monthly_data(Share_Data, symbol):
    Table_Month = []
    for j in Share_Data["TIMESTAMP"].dt.year.unique():
        include = Share_Data[Share_Data["TIMESTAMP"].dt.year == j]
        for months in include["TIMESTAMP"].dt.month.unique():
            Monthly_close = []
            Monthly_close.append(j)
            Monthly_close.append(months)
            Monthly_close.append(symbol)
            include_month = include[include["TIMESTAMP"].dt.month == months]
            Min_Value = (
                include_month["CLOSE"]
                .loc[(include_month["TIMESTAMP"] == include_month["TIMESTAMP"].min())]
                .reset_index()
                .iloc[0]["CLOSE"]
            )
            Max_Value = (
                include_month["CLOSE"]
                .loc[(include_month["TIMESTAMP"] == include_month["TIMESTAMP"].max())]
                .reset_index()
                .iloc[0]["CLOSE"]
            )
            Monthly_close.append(((Max_Value - Min_Value) / Min_Value) * 100)
            Table_Month.append(Monthly_close)
    Close_Month_Table = pd.DataFrame(
        Table_Month, columns=["Year", "Months", "Symbol", "%Change_Closing_Price"]
    )
    Close_Month_Table = Close_Month_Table.sort_values(by=["Months"], ascending=True)
    #    Close_Month_Table['Months'] = Close_Month_Table['Months'].apply(lambda x: calendar.month_abbr[x])
    return Close_Month_Table


def sector_wise_yearly_returns(data, sec):
    data = data[data["SECTOR"] == sec]
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    new_data = pd.DataFrame()
    for i in data["SYMBOL"].unique():
        Data = sector_yearly_data(data[data["SYMBOL"] == i], i)
        new_data = new_data.append(Data)
    return new_data


def sector_wise_monthly_returns(data, sec):
    data = data[["TIMESTAMP", "SYMBOL", "CLOSE", "SECTOR"]]
    data = data[data["SECTOR"] == sec]
    data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])
    new_data = pd.DataFrame()
    for i in data["SYMBOL"].unique():
        Data = sector_monthly_data(data[data["SYMBOL"] == i], i)
        new_data = new_data.append(Data)
    return new_data


def generate_analysis2(sec):
    end_date = datetime.datetime.today()
    start_date = datetime.datetime.now() - datetime.timedelta(days=5 * 365)
    start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
    sector = load_sector_data("cash_market", end_date, start_date)
    print(sector)
    sectors = sector["SECTOR"].unique()
    print(sectors)

    yearly_df = sector_wise_yearly_returns(sector, sec)
    pivot_table = yearly_df.pivot(
        index="Symbol", columns="Year", values="%Change_Closing_Price"
    )
    fig1 = go.Figure(data=go.Heatmap(df_to_plotly(pivot_table), colorscale="Viridis"))
    fig1.update_layout(
        height=300,
        font=dict(size=10),
        xaxis=dict(tickmode="linear"),
        yaxis=dict(tickmode="linear"),
    )
    fig1.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    fig1.update_layout(
        title="Plot Title",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )

    monthly_df = sector_wise_monthly_returns(sector, sec)
    year_v = monthly_df["Year"].unique()
    print(year_v)
    year_d = start_date.year
    final_years = monthly_df[monthly_df["Year"] == year_d]
    pivot_table = final_years.pivot(
        index="Symbol", columns="Months", values="%Change_Closing_Price"
    )
    print(pivot_table)
    fig2 = go.Figure(data=go.Heatmap(df_to_plotly(pivot_table), colorscale="Viridis"))
    fig2.update_layout(
        height=300,
        font=dict(size=10),
        xaxis=dict(tickmode="linear"),
        yaxis=dict(tickmode="linear"),
    )
    fig2.update_xaxes(
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        )
    )
    fig2.update_layout(
        title="Plot Title",
        xaxis_title="X Axis Title",
        yaxis_title="Y Axis Title",
        font=dict(family="sans serif, monospace", size=15, color="RebeccaPurple"),
    )
    return fig1, fig2


def generate_analysis3(ticker):
    return
