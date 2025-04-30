import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BUY_THRESHOLD = 0.05
SELL_THRESHOLD = -0.05
START_DATE = "2020-01-02"
END_DATE = "2022-01-01"
INITIAL_CAPITAL = 10000

# Read selected stock pairs
pairs = []
with open("selected_pairs.txt", "r") as f:
    for line in f:
        leader, lagger = line.strip().split()
        pairs.append((leader, lagger))


# Get all unique tickers
tickers = list(set([s for pair in pairs for s in pair]))
# Download historical data
raw_data = yf.download(tickers, start=START_DATE, end=END_DATE)




sp_data = yf.download('SPY', start=START_DATE, end=END_DATE)

first_valid_date = sp_data.index[1]

# Get the opening price
opening_price = int(sp_data.loc[first_valid_date, 'Open'])

# Calculate number of shares for spy 
spy_shares = INITIAL_CAPITAL / opening_price


sp_close = sp_data['Close']
open_data = raw_data['Open']
data = raw_data['Close']

# Fill forward to handle any missing days (suspensions)
data = data.fillna(method='ffill')
open_data = data.fillna(method='ffill')

# Portfolio tracking
portfolio_value = pd.Series(index=data.index, dtype=float)
sp_value = pd.Series(index=sp_data.index, dtype=float)

cash = INITIAL_CAPITAL
positions = {}
for _, lagger in pairs:
    positions[lagger] = 0

# Daily loop
buy = False
sell = False
for i in range(1, len(data.index)):
    date = data.index[i]
    prev_date = data.index[i - 1]

    for leader, lagger in pairs:
        if leader not in data.columns or lagger not in data.columns:
            continue

        lagger_price = open_data.loc[date, lagger]

        if buy:
            cash -= lagger_price
            positions[lagger] += 1
            print(f"{date.date()}: BUY 1 share of {lagger} because {leader} rose {pct_change:.2%}")

        elif sell:
            cash += lagger_price
            positions[lagger] -= 1
            print(f"{date.date()}: SELL 1 share of {lagger} because {leader} fell {pct_change:.2%}")


        leader_price_today = data.loc[date, leader]
        leader_price_yesterday = data.loc[prev_date, leader]
        pct_change = (leader_price_today - leader_price_yesterday) / leader_price_yesterday

        if pct_change >= BUY_THRESHOLD:
            buy = True
            sell = False

        elif pct_change <= SELL_THRESHOLD:
            buy = False
            sell = True

        else:
            buy = False
            sell = False

    # Calculate portfolio value
    total_value = cash
    for lagger, shares in positions.items():
        price = data.loc[date, lagger]
        total_value += (price * shares)
    portfolio_value[date] = total_value
    sp_value[date] = sp_close.loc[date] * spy_shares

# Plot performance
ax = portfolio_value.plot(title="Strategy Portfolio Value", figsize=(10, 5), label="Lead-Lag Portfolio")
sp_value.plot(ax=ax, title="Strategy Performance", figsize=(10, 5), label="SPY Portfolio")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.xlabel("Date")
plt.grid(True)
plt.tight_layout()

plt.show()


# Compute running maximum
running_max = portfolio_value.cummax()
spy_running_max = sp_value.cummax()

# Compute Sharpe Ratio
returns = portfolio_value.pct_change().dropna()
sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()

spy_returns = sp_value.pct_change().dropna()
spy_sharpe = np.sqrt(252) * spy_returns.mean() / spy_returns.std()
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"SPY Sharpe Ratio: {spy_sharpe:.2f}")


