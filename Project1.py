import pandas as pd
import yfinance as yf
import datetime
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
def get_index_components():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {'class': 'wikitable'})
    rows = table.find_all('tr')[1:]

    tickers = []

    for row in rows:
        columns = row.find_all(['td', 'th'])
        ticker = columns[0].text.strip()
        tickers.append(ticker)

    return tickers

def get_price_data(tickers, start, end):
    data = {}
    for ticker in tickers:
        ticker_data = yf.download(ticker, start=start, end=end, interval='1d')['Close']
        data[ticker] = ticker_data
    return pd.DataFrame(data)

def calculate_pmcc(tickers_data, index_data):
    correlations = {}
    for ticker in tickers_data.columns:
        correlations[ticker] = tickers_data[ticker].corr(index_data)
    return correlations

def sort(array):
    sorted_array = sorted(array.items(), key=lambda x: x[1], reverse=True)
    return sorted_array

def plot_price_date():
    plt.figure(figsize=(14, 7))

    for ticker in top_10_tickers[0]:
        ticker_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')['Close']
        plt.plot(ticker_data.index, ticker_data.values, label=ticker)

    plt.plot(index_data.index, index_data.values, label=index_ticker, linewidth=3, color='black')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(bbox_to_anchor = (0.75,1.15), ncol = 2)
    plt.grid(True)
    plt.show()

def calculate_pairwise_rolling_pmcc(ticker_pairs, start_date, end_date, interval='1d'):
    correlations_df = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))

    for pair in ticker_pairs:
        ticker1_data = yf.download(pair[0], start=start_date, end=end_date, interval=interval)['Close']
        ticker2_data = yf.download(pair[1], start=start_date, end=end_date, interval=interval)['Close']

        joined_data = pd.concat([ticker1_data, ticker2_data], axis=1, join='inner')
        joined_data.columns = pair

        rolling_correlations = joined_data.rolling(window=60).corr().unstack().iloc[:,1].dropna()

        correlations_df[f'{pair[0]} - {pair[1]}'] = rolling_correlations

    correlations_df = correlations_df.dropna(how='all')

    return correlations_df

def plot_rolling_correlations():
    plt.figure(figsize=(14, 7))

    for pair in rolling_pair_pmcc_df:
        plt.plot(rolling_pair_pmcc_df.index, rolling_pair_pmcc_df[pair], label=pair)

    plt.xlabel('Date')
    plt.ylabel('Correlation')
    plt.legend(bbox_to_anchor = (0.75,1.15), ncol = 2)
    plt.show()

index_ticker = '^GSPC'
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime.now()
price_data = get_price_data(get_index_components(), start_date, end_date)
index_data = yf.download(index_ticker, start=start_date, end=end_date, interval='1d')['Close']
correlations = calculate_pmcc(price_data, index_data)
sorted_correlations_df = pd.DataFrame(sort(correlations))
top_10_tickers = sorted_correlations_df.head(10)

top_10_tickers_data = get_price_data(top_10_tickers[0], start_date, end_date)
sorted_tickers = top_10_tickers_data.columns.tolist()

ticker_pairs = list(zip(sorted_tickers[::2], sorted_tickers[1::2]))
rolling_pair_pmcc_df = calculate_pairwise_rolling_pmcc(ticker_pairs, start_date, end_date, interval='1d')
