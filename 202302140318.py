import ccxt
import pandas as pd
import numpy as np
import os
from datetime import date, datetime, timezone, tzinfo
import time
import warnings


warnings.filterwarnings("ignore")


symbol = "ETH/BUSD"  # Binance
greater_volume = 150
pos_size = 1
timeframe = "1m"
ex = ccxt.binance()
from_ts = ex.parse8601('2023-02-12 00:00:00')
next_ts = ex.parse8601('2023-02-12 12:00:00')
# API
account_binance = ccxt.binance({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": True,
    'options': {
        'defaultType': 'spot'
    }
})
 # 1 day = 60*60 =1440 mins max row counts is 1000, so first part = 720 rows, second part =720 rows
first_ohlcvLB = account_binance.fetch_ohlcv(symbol, timeframe, since=from_ts, limit=720)
second_ohlcvLB = account_binance.fetch_ohlcv(symbol, timeframe,since=next_ts, limit=720)
df1 = pd.DataFrame(first_ohlcvLB, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
df2 = pd.DataFrame(second_ohlcvLB, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
if len(first_ohlcvLB):
    df1['time'] = pd.to_datetime(df1['time'], unit='ms')
if len(second_ohlcvLB):
    df2['time'] = pd.to_datetime(df2['time'], unit='ms')
# exclude markets with volume less than 1,500,000, now greater_volume=150
data1 = df1[(df1['volume'] > greater_volume)]
data2 = df2[(df2['volume'] > greater_volume)]
data = data1.append(data2, ignore_index=True)


#Calculate percent change between close[1] and close
data['close_1min_ago'] = data['close'].shift(1)
data['pct_change'] = abs((data['close'] - data['close_1min_ago'])) / data['close_1min_ago'] * 100


#Calculate percent change2 between open and close
data['pct_change2'] = abs((data['close'] - data['open'])) / data['open'] * 100


# the first 20 coins in order of the highest percentage change
data.sort_values(by='pct_change',ascending=True)[0:20]
# get  pct_change ascending  20 rows
final_pc_change = data.sort_values(by='pct_change',ascending=True)[0:20]
# get  pct_change2 ascending  20 rows
final_pc_change2 = data.sort_values(by='pct_change2',ascending=True)[0:20]
# output
print(final_pc_change)
print('----------------------------------------------')
print(final_pc_change2)



