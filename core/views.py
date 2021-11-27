from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from plotly.offline import plot
from django.http import JsonResponse
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import json, os
import pandas as pd
from pandas_datareader import data as pdr
from django.conf import settings
import datetime
from bs4 import BeautifulSoup
import requests
from .graphPlots import (
    load_data_realtime,
    generate_analysis1,
    generate_analysis2,
)
import logging
import adal
from .util import get_settings


get_settings()

date = datetime.date.today()
log = logging.getLogger()
log.debug("Env vars: \n" + str(os.getenv))


# landing page
def home(request):
    return render(request, "core/home.html", {"date": date})


# signup user
def signupuser(request):
    if request.method == "GET":
        return render(
            request, "core/signupuser.html", {"form": UserCreationForm(), "date": date}
        )
    else:
        # Create a new user
        if request.POST["password1"] == request.POST["password2"]:
            try:
                email = request.POST["email"].lower()
                r = User.objects.filter(email=email)
                if r.count():
                    return render(
                        request,
                        "core/signupuser.html",
                        {"error": "Email already exists"},
                    )
                else:
                    user = User.objects.create_user(
                        request.POST["username"],
                        password=request.POST["password1"],
                        email=request.POST["email"],
                    )
                    user.save()
                    login(request, user)
                    return redirect("stockdata")
            except IntegrityError:
                return render(
                    request,
                    "core/signupuser.html",
                    {
                        "error": "This username has already been taken. Please choose a new Username",
                        "date": date,
                    },
                )
            except ValueError:
                return render(
                    request,
                    "core/signupuser.html",
                    {"error": "Please enter valid username", "date": date},
                )
        else:
            # tell the user the password didn't match
            return render(
                request,
                "core/signupuser.html",
                {"error": "Passwords did not match", "date": date},
            )


# login user
def loginuser(request):
    if request.method == "GET":
        return render(
            request, "core/loginuser.html", {"form": AuthenticationForm(), "date": date}
        )
    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user is None:
            return render(
                request,
                "core/loginuser.html",
                {
                    "form": AuthenticationForm(),
                    "error": "User password did not match",
                    "date": date,
                },
            )
        else:
            login(request, user)
            return redirect("stockdata")


# logout user
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")


# realtime stockdata table
def stockdata(request):
    print("starting.......")
    stock_symbols = pd.read_csv(
        os.path.join(settings.BASE_DIR, "core", "stock_symbols.csv")
    )
    all_stock_codes = stock_symbols.Symbol.tolist()
    all_tickers = [x + ".NS" for x in all_stock_codes[0:5]]
    all_tickers = ",".join([elem for elem in all_tickers])

    yf.pdr_override()
    data = pdr.get_data_yahoo(
        tickers=all_tickers,
        period="1d",
        interval="1d",
        group_by="ticker",
        threads=False,
    )
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

    res = data.to_json(orient="columns", double_precision=2)
    res = json.loads(res)
    res_without_NS = dict()
    for key, value in res.items():
        t = key.split(".")
        data = load_data_realtime("dump_52wk", t[0])
        try:
            # value["perChange"]=
            value["52WH"] = data["52WKH"].values[0]
            value["52WL"] = data["52WKL"].values[0]
            value["10DH"] = data["10DH"].values[0]
            value["10DL"] = data["10DL"].values[0]
            value["1MAV"] = int(data["1MV"].values[0])
            value["VM"] = int(value["Volume"] / value["1MAV"])
        except:
            value["52WH"] = 0
            print("data not found")
        df_sec = stock_symbols[stock_symbols["Symbol"] == t[0]]
        value["Sector"] = df_sec.iloc[0].at["Industry"]
        res_without_NS[t[0]] = value
    return render(
        request,
        "core/stockdata.html",
        {"stocks": res_without_NS, "date": date},
    )


def graphs(request, ticker):
    print("graphs loading.....")
    dataInf = yf.Ticker(ticker + ".NS")
    data = yf.download(
        tickers=ticker + ".NS",
        period="1d",
        interval="1m",
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("OHLC", "Volume"),
        row_width=[0.2, 0.7],
    )
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="OHLC",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=data.index, y=data["Volume"], showlegend=False), row=2, col=1
    )

    # Add dropdown
    fig.update_layout(
        transition_duration=2000,
        autosize=True,
        title="The Great Recession",
        yaxis_title=ticker + " Stock",
        xaxis_rangeslider_visible=False,
        updatemenus=[
            dict(
                buttons=list(
                    [
                        dict(
                            args=["type", "candlestick"],
                            label="Candlestick",
                            method="restyle",
                        ),
                        dict(
                            args=["type", "scatter"], label="scatter", method="restyle"
                        ),
                    ]
                ),
                # direction="down",
                # pad={"r": 10, "t": 10},
                # showactive=True,
                # x=0.03,
                # xanchor="right",
                # y=1.3,
                # yanchor="bottom",
            ),
        ],
    )

    plot_div = plot(fig, output_type="div")
    info = dataInf.info
    info["close"] = int(data["Close"].tail(1))
    df = data
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()
    EMA_20 = int(df["EMA_20"].tail(1))
    EMA_50 = int(df["EMA_50"].tail(1))
    EMA_200 = int(df["EMA_200"].tail(1))

    delta = df["Close"].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()

    relative_strength = ema_up / ema_down
    RSI = 100 - (100 / (1 + relative_strength))
    rsi_value = int(RSI.tail(1))
    # print(rsi_value)

    print(df)
    try:
        Pe = int((dataInf.info["forwardPE"]))
        Eps = int((dataInf.info["forwardEps"]))
        TEps = int((dataInf.info["trailingEps"]))
        PI = int((dataInf.info["heldPercentInsiders"]) * 100)
        FI = int((dataInf.info["heldPercentInstitutions"]) * 100)
    except:
        Pe = 0
        Eps = 0
        TEps = 0
        PI = 0
        FI = 0
    Others = 100 - (PI + FI)
    label = ["Promoter Holdings", "Foreign Holdings", "Others"]
    holdings = [PI, FI, Others]
    fig = go.Figure(data=[go.Pie(labels=label, values=holdings)])
    plot_div1 = plot(fig, output_type="div")

    stock_url = "https://www.screener.in/company/" + ticker + "/"
    response = requests.get(stock_url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        ROE = soup.find_all("span", {"class": "number"})[8].text
    except:
        ROE = None
    dfr = pd.DataFrame(
        {
            "Year": [
                "Mar-10",
                "Mar-11",
                "Mar-12",
                "Mar-13",
                "Mar-14",
                "Mar-15",
                "Mar-16",
                "Mar-17",
                "Mar-18",
                "Mar-19",
                "Mar-20",
                "Mar-21",
            ]
        }
    )

    net_profit = []

    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[23].find_all("td")[i].text
            com = com.replace(",", "")
            net_profit.append(int(com))
        except:
            net_profit.append(None)

    eps = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[24].find_all("td")[i].text
            eps.append(float(com))
        except:
            eps.append(None)
    sales = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[14].find_all("td")[i].text
            com = com.replace(",", "")
            sales.append(int(com))
        except:
            sales.append(None)
    equity = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[47].find_all("td")[i].text
            com = com.replace(",", "")
            equity.append(int(com))
        except:
            equity.append(None)
    reserves = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[48].find_all("td")[i].text
            com = com.replace(",", "")
            reserves.append(int(com))
        except:
            reserves.append(None)
    borrowings = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[49].find_all("td")[i].text
            com = com.replace(",", "")
            borrowings.append(int(com))
        except:
            borrowings.append(None)
    liabilities = []
    for i in range(1, 13):
        try:
            com = soup.find_all("tr")[50].find_all("td")[i].text
            com = com.replace(",", "")
            liabilities.append(int(com))
        except:
            liabilities.append(None)

    dfr["NetProfit"] = net_profit
    dfr["Sales"] = sales
    dfr["EPS"] = eps
    dfr["equity"] = equity
    dfr["reserves"] = reserves
    dfr["borrowings"] = borrowings
    dfr["liabilities"] = liabilities
    dfr["DE"] = (dfr["borrowings"] + dfr["liabilities"]) / (
        dfr["equity"] + dfr["reserves"]
    )
    financial_dataframe = dfr[["Year", "NetProfit", "Sales", "EPS", "DE"]]
    financial_dataframe = financial_dataframe.to_json(
        orient="index", double_precision=2
    )
    financial_dataframe = json.loads(financial_dataframe)

    return render(
        request,
        "core/graphs.html",
        {
            "date": date,
            "info": info,
            # "financial_dataframe":financial_dataframe,
            "info1": PI,
            "info2": FI,
            "info3": Pe,
            "info4": Eps,
            "info5": TEps,
            "EMA20": EMA_20,
            "EMA50": EMA_50,
            "EMA200": EMA_200,
            "plot_div": plot_div,
            "rsi": rsi_value,
            "ROE": ROE,
            "plot_pie": plot_div1,
        },
    )

    # return render(request, "core/graphs.html", context={"plot_div": plot_div,"info":dataInf.info,"date": date})


def analysis1(request, ticker):
    (
        plotly_figure1,
        plotly_figure2,
        plotly_figure3,
        plotly_figure4,
        plotly_figure5,
        plotly_figure6,
        plotly_figure7,
        plotly_figure8,
        corr_figure1,
        fig,
    ) = generate_analysis1(ticker)
    plot_div1 = plot(plotly_figure1, output_type="div", config={"displaylogo": False})
    plot_div2 = plot(plotly_figure2, output_type="div")
    plot_div3 = plot(plotly_figure3, output_type="div")
    plot_div4 = plot(plotly_figure4, output_type="div")
    plot_div5 = plot(plotly_figure5, output_type="div")
    plot_div6 = plot(plotly_figure6, output_type="div")
    plot_div7 = plot(plotly_figure7, output_type="div")
    plot_div8 = plot(plotly_figure8, output_type="div")
    corr_fig1 = plot(corr_figure1, output_type="div")
    fig = plot(fig, output_type="div")
    return render(
        request,
        "core/analysis1.html",
        context={
            "date": date,
            "plot_div1": plot_div1,
            "plot_div2": plot_div2,
            "plot_div3": plot_div3,
            "plot_div4": plot_div4,
            "plot_div5": plot_div5,
            "plot_div6": plot_div6,
            "plot_div7": plot_div7,
            "plot_div8": plot_div8,
            "corr_fig1": corr_fig1,
            "fig": fig,
        },
    )


def analysis2(request, sec):
    (
        plotly_figure1,
        plotly_figure2,
    ) = generate_analysis2(sec)
    plot_div1 = plot(plotly_figure1, output_type="div", config={"displaylogo": False})
    plot_div2 = plot(plotly_figure2, output_type="div")

    return render(
        request,
        "core/analysis1.html",
        context={
            "date": date,
            "plot_div1": plot_div1,
            "plot_div2": plot_div2,
        },
    )
