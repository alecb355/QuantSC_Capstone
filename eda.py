import pandas as pd
import os
import glob
import numpy as np

# Define the directory containing CSV files
data_dir = "data/"

# Get a list of all CSV files in the directory
csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

# Load each CSV into a dictionary with the stock ticker as the key
stock_data = {}

for file in csv_files:
    ticker = os.path.basename(file).replace(".csv", "")  # Extract ticker from filename
    stock_data[ticker] = pd.read_csv(file, index_col="Date")

# Print loaded tickers
# print(f"Loaded {len(stock_data)} stock files: {list(stock_data.keys())}")

for ticker, df in stock_data.items():
    df["Return"] = df["Close"].pct_change()

stock_list = list(stock_data.items())

# Delta threshold for determining lead-lag link
delta = 0.2

# Matrix for each stock by each stock in S&P. Not 500 because some stocks have been delisted.
matrix = np.zeros((488, 488))



# Day 1000
day = pd.Timestamp('2019-04-01')
# day = '2019-12-03'

# i is the lagger, j is the leader
for t in range(31):
    new_date = day + pd.Timedelta(days=t)
    formatted_date = new_date.strftime('%Y-%m-%d')
    for i in range(488):
        if formatted_date in stock_list[i][1].index:
            i_return = stock_list[i][1].loc[formatted_date, "Return"]
            for j in range(488):
                if formatted_date in stock_list[j][1].index:
                    j_return = stock_list[j][1].loc[formatted_date, "Return"]
                    if i_return >= (1 - delta) * j_return and i_return <= j_return * (1 + delta):
                        matrix[i][j] += 1
        matrix[i][i] = 0

flat_indices = np.argsort(matrix, axis=None)[-10:]  # Get the indices of the 10 largest values


flat_indices = flat_indices[::-1]
# Convert flat indices to row, column indices
rows, cols = np.unravel_index(flat_indices, matrix.shape)

# Print the 10 largest values along with their row and column indices. Row is lagger, Col is leader
for i in range(10):
    print("Leader: ", stock_list[cols[i]][0], ", Lagger: ", stock_list[rows[i]][0])
    print(f"Value: {matrix[rows[i], cols[i]]} at row {rows[i]}, column {cols[i]}")


np.savetxt("matrix.txt", matrix, fmt = "%d")
