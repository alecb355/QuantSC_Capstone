import yfinance as yf
import pandas as pd
import os
import time

# Gets the S&P500 tickers from Wikipedia
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)
    sp500_tickers = table[0]["Symbol"].tolist()
    return sp500_tickers

def fetch_all_prices(batch_size = 50):

    # start and end dates
    start_date = "2010-01-01"
    start_ts = pd.Timestamp(start_date)

    end_date = "2020-01-01"
    end_ts = pd.Timestamp(end_date)

    # Get prices for S&P 500 IDX
    sp_idx = yf.Ticker("^GSPC")
    sp_idx_data = sp_idx.history(start=start_ts, end=end_ts, interval = "1d")
    sp_idx_data.to_csv("sp500_prices.csv")

    # Get tickers for individual stocks
    tickers = get_sp500_tickers()

    # create data dir
    os.makedirs("data", exist_ok=True)
    
    # Process stocks in batches to avoid rate limits
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"Fetching batch {i // batch_size + 1} / {len(tickers) // batch_size + 1}")
        try:
            data = yf.download(batch, start=start_date, end=end_date, interval="1d", group_by="ticker")
        except Exception as e:
            print(f"Error fetching batch {i // batch_size + 1}: {e}")
            continue
        
        for ticker in batch:
            if ticker in data.columns.levels[0]:  # Ensure valid data exists
                stock_data = data[ticker].dropna()  # Remove empty rows
                if not stock_data.empty:
                    stock_data.to_csv(f"data/{ticker}.csv")

        time.sleep(2)  # Pause to prevent rate limits for yf

    print("All available S&P 500 stock data saved!")


if __name__ == "__main__":
    fetch_all_prices()

