# DAX Stock Visualizer.
# Simple webapp powered by Streamlit,
# plotting adjustable price charts as well as information on major/institutional holders
# for components of the german DAX stock index.
#
# How to run:
# 1. Open terminal and cd to where 'DAX_Visualizer.py' is located
# 2. "streamlit run DAX_Visualizer.py"


import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st


# Scraping company names and ticker symbols.
def load_tickers(url, num=0):
    html = pd.read_html(url)
    table = html[num]

    tickers = pd.DataFrame()
    tickers["Company"] = table["Company"]
    tickers["Ticker"] = table["Ticker symbol"]
    tickers.set_index("Company", inplace=True)
    return tickers


# Downloading price and volume data from Yahoo Finance, adding RSI indicator to dataframe, dropping NA values.
@st.cache(allow_output_mutation=True)
def load_price_data(ticker, start, end, interval):
    data = yf.download(tickers=ticker, start=start, end=end, interval=interval)
    data[f"RSI ({rsi_periods})"] = rsi(data["Adj Close"], rsi_periods)
    data.dropna(inplace=True)
    return data


# Calculating RSI indicator.
def rsi(series, periods):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    ema_up = up.ewm(com=periods-1, adjust=False).mean()
    ema_down = down.ewm(com=periods-1, adjust=False).mean()
    
    rs = ema_up / ema_down
    rsi = 100 - (100/(1+rs))
    return rsi


# Calculating simple moving averages(SMA).
def sma(series, period):
    sma = series.rolling(period).mean()
    return sma


# Downloading data on major holders from Yahoo Finance.
@st.cache(allow_output_mutation=True)
def load_major_holders(ticker):
    stock = yf.Ticker(ticker)
    return stock.major_holders


# Downloading data on institutional holders from Yahoo Finance.
@st.cache(allow_output_mutation=True)
def load_institutional_holders(ticker):
    stock = yf.Ticker(ticker)
    institutional_holders = stock.institutional_holders
    institutional_holders.drop(columns="Value", inplace=True)
    return institutional_holders


# Converting selectbox input for load_price_data().
def convert_interval(interval):
    interval = "1d" if interval == "1 day" else interval
    interval = "1wk" if interval == "1 week" else interval
    interval = "1mo" if interval == "1 month" else interval
    return interval


# Creating price chart and subplots.
def plot_price(price_data):
    df = price_data
    df["Date"] = df.index

    plt.figure(figsize=(12,8))
    
    ax1 = plt.subplot(14, 1, (1,7))
    ax1.plot(df.index, df["Adj Close"], color="lightgray", linewidth=2, label="Adj. Close")
    ax1.grid(True, color="#555555")
    ax1.set_facecolor("black")
    ax1.figure.set_facecolor("#121212")
    ax1.tick_params(axis="x", colors="white")
    ax1.tick_params(axis="y", colors="white")
  
    if sma_1:
        sma_1_plot = sma(df["Adj Close"], sma_1_periods)
        ax1.plot(df.index, sma_1_plot, color=SMA_1_COLOR, alpha=0.8, linewidth=2, label=f"SMA({sma_1_periods})")

    if sma_2:
        sma_2_plot = sma(df["Adj Close"], sma_2_periods)
        ax1.plot(df.index, sma_2_plot, color=SMA_2_COLOR, alpha=0.8, linewidth=2, label=f"SMA({sma_2_periods})")

    ax1.legend(facecolor="#121212", labelcolor="white")

    if rsi_1:
        ax2 = plt.subplot(14, 1, (9,10), sharex=ax1)
        ax2.plot(df.index, df[f"RSI ({rsi_periods})"], color="lightgray")
        ax2.set_title(f"RSI ({rsi_periods})", color="white")
        ax2.grid(True, color="#555555")
        ax2.set_facecolor("black")
        ax2.tick_params(axis="x", colors="#121212")
        ax2.tick_params(axis="y", colors="white")
        ax2.set_yticks(ticks=[0,30,70,100])
        ax2.axhline(1, linestyle="--", alpha=0.5, color=RSI_0_100_COLOR)
        ax2.axhline(99, linestyle="--", alpha=0.5, color=RSI_0_100_COLOR)
        ax2.axhline(15, linestyle="--", alpha=0.5, color=RSI_15_85_COLOR)
        ax2.axhline(85, linestyle="--", alpha=0.5, color=RSI_15_85_COLOR)
        ax2.axhline(30, linestyle="--", alpha=0.5, color=RSI_30_70_COLOR)
        ax2.axhline(70, linestyle="--", alpha=0.5, color=RSI_30_70_COLOR)

    if volume:
        if rsi_1:
            ax3 = plt.subplot(14, 1, (12,14), sharex=ax1)
        else:
            ax3 = plt.subplot(14, 1, (9,10), sharex=ax1)
        ax3.bar(df.index, df["Volume"], color="white")
        ax3.set_title("Volume", color="white")
        ax3.grid(True, color="#555555")
        ax3.set_facecolor("black")
        ax3.tick_params(axis="x", colors="white")
        ax3.tick_params(axis="y", colors="white")
    
    return st.pyplot()


# Creating pie charts for major holders.
def plot_major_holders(major_holders): 
    ptc_insiders = float((major_holders[0][0])[:-1])
    ptc_shares_institutions = float((major_holders[0][1])[:-1])
    ptc_float_institutions = float((major_holders[0][2])[:-1])

    plt.figure(figsize=(12,8))

    ax1 = plt.subplot(1, 5, 1)
    ax1.pie([ptc_insiders,100-ptc_insiders], colors=["black","white"], 
            labels=[major_holders[0][0],None], counterclock=False, startangle=90, wedgeprops={"edgecolor":"k"})
    ax1.set_title("% of Shares Held by Insiders")

    ax2 = plt.subplot(1, 5, 3)
    ax2.pie([ptc_shares_institutions,100-ptc_shares_institutions], colors=["black","white"],
            labels=[major_holders[0][1],None], counterclock=False, startangle=90, wedgeprops={"edgecolor":"k"})
    ax2.set_title("% of Shares Held by Institutions")

    ax3 = plt.subplot(1, 5, 5)
    ax3.pie([ptc_float_institutions,100-ptc_float_institutions], colors=["black","white"], 
            labels=[major_holders[0][2],None], counterclock=False, startangle=90, wedgeprops={"edgecolor":"k"})
    ax3.set_title("% of Float Held by Institutions")

    return st.pyplot()


# Setting variables.
URL = "https://en.wikipedia.org/wiki/DAX"
TABEL_NUM = 3
TICKERS = load_tickers(URL, TABEL_NUM)
SMA_1_COLOR = "#ffd700"
SMA_2_COLOR = "#2069e0"
RSI_30_70_COLOR = "#00ff00"
RSI_15_85_COLOR = "#ffaa00"
RSI_0_100_COLOR = "#ff0000"
sma_1_periods = 50
sma_2_periods = 200
rsi_periods = 14


# Streamlit page config.
st.set_page_config(layout="wide", page_title="DAX Stock Visualizer", page_icon="🚀")
st.set_option('deprecation.showPyplotGlobalUse', False)
col1 , col2 = st.columns((1,10))

# Sidebar config.
st.sidebar.title("DAX Stock Visualizer")
stock = st.sidebar.selectbox("Select stock:", TICKERS.index)
ticker = TICKERS["Ticker"][str(stock)]
start_date = st.sidebar.date_input("Select start date:", value=pd.to_datetime("2019-01-01"), min_value=pd.to_datetime("2000-01-01"))
end_date = st.sidebar.date_input("Select end date:", min_value=start_date)
interval = st.sidebar.selectbox("Select interval:", ["1 day", "1 week", "1 month"], index = 0)
sma_1 = st.sidebar.checkbox("Simple Moving Average (SMA)", value=True, key=1)
sma_1_periods = st.sidebar.slider("Pick number of periods:", min_value=5, max_value=200, value=50)
sma_2 = st.sidebar.checkbox("Simple Moving Average (SMA)", value=True, key=2)
sma_2_periods = st.sidebar.slider("Pick number of periods:", min_value=5, max_value=200, value=200)
rsi_1 = st.sidebar.checkbox("Relative Strength Indxex (RSI)", value=True)
rsi_periods = st.sidebar.slider("Pick number of periods:", min_value=5, max_value=50, value=14)
volume = st.sidebar.checkbox("Volume", value=True)

# Converting interval and loading Data.
converted_interval = convert_interval(interval)
price_data = load_price_data(ticker, start_date, end_date, converted_interval)
institutional_holders = load_institutional_holders(ticker)
major_holders  = load_major_holders(ticker)


# Plotting data to column 2 of main page.
with col2:
    st.title(f"{stock} ({ticker})")

    st.subheader("Price Chart")
    plot_price(price_data)

    st.subheader("Major Holders")
    plot_major_holders(major_holders)

    st.subheader("Institutional Holders")
    institutional_holders

    st.subheader("Price Data")
    if st.button('Show Dataframe'):
        st.header(f"{stock}: {start_date} - {end_date}, Interval: {interval}")
        st.write("Source: Yahoo Finance")
        price_data