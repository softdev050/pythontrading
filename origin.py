

import pandas as pd
import numpy as np
import talib
import time
from binance.client import Client
import pytz
from datetime import datetime, timedelta

client = Client("api_key", "secret_key")

# Request count
count = 0

# Get historical klines (candlesticks) of specific symbol and interval
klines = client.get_historical_klines("SYSUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

# Store klines in dataframe
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignored'])
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Set timestamp as index
df.set_index('timestamp', inplace=True)



# Convert timestamp to UTC+1 timezone
df.index = df.index.tz_localize(pytz.UTC).tz_convert(pytz.timezone("Europe/Berlin"))

#Calculate EMA 10, EMA 20, EMA 50, EMA 100 and EMA 200
df['ema_10'] = talib.EMA(df['close'], timeperiod=10)
df['ema_20'] = talib.EMA(df['close'], timeperiod=20)
df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
df['ema_100'] = talib.EMA(df['close'], timeperiod=100)
df['ema_200'] = talib.EMA(df['close'], timeperiod=200)

#Calculate MACD
macd, macd_signal, macd_hist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
df['macd'] = macd
df['macd_signal'] = macd_signal
df['macd_hist'] = macd_hist

#Calculate Fast MACD
fmacd, fmacd_signal, fmacd_hist = talib.MACD(df['close'], fastperiod=3, slowperiod=10, signalperiod=3)
df['fmacd'] = fmacd
df['fmacd_signal'] = fmacd_signal
df['fmacd_hist'] = fmacd_hist



# Convert close and ema_10 to float
df['close'] = df['close'].astype(float)
df['ema_10'] = df['ema_10'].astype(float)

#Convert macd to float
df['macd'] = df['macd'].astype(float)

#Convert fmacd to float
df['fmacd'] = df['fmacd'].astype(float)




# Create a column to check if the close price is greater than EMA 10
df['ema10up'] = np.where(df['close'] >= df['ema_10'], True, False)

#Create a column to check if the MACD is greater than 0
df['macdup'] = np.where(df['macd'] >= 0, True, False)

#Create a column to check if Fast MACD is greater than 0
df['fmacdup'] = np.where(df['fmacd'] >= 0, True, False)


#Create a column to check if either MACD or Fast MACD is greater than 0
df['totmacd'] = np.where((df['macdup'] == True) | (df['fmacdup'] == True), True, False)


# Create a column to check if the uptrend is present
df['emauptrend'] = np.where((df['ema_10'] >= df['ema_20']) & (df['ema_20'] >= df['ema_50']) & (df['ema_50'] >= df['ema_100']) & (df['ema_100'] >= df['ema_200']), True, False)

#Calculate percentage change
df['open'] = df['open'].astype(float)
df['close'] = df['close'].astype(float)
#Calculate percent change between close[1] and close
df['close_1min_ago'] = df['close'].shift(1)
df['pct_change'] = (df['close'] - df['close_1min_ago']) / df['close_1min_ago'] * 100
#Calculate percent change2 between open and close
df['pct_change2'] = (df['close'] - df['open']) / df['open'] * 100

#calculate percent change total > 1%
Percent_changetot = (df['pct_change'] >= 1) | (df['pct_change2'] >= 1)

#Get last 1 complete bars (without the current bar)
last_1 = df.iloc[-2:-1, :]

# Print result
print(last_1[['close', 'ema_10', 'ema_20', 'ema_50', 'ema_100', 'ema_200', 'quote_asset_volume', 'ema10up', 'emauptrend',  'macd', 'macdup', 'fmacd', 'fmacdup', 'totmacd']])
print("Percent change: {:.4f}%".format(last_1['pct_change'].values[0]))
print("Percent change2: {:.4f}%".format(last_1['pct_change2'].values[0]))
if Percent_changetot.values[0]:
    print("Percent_changetot: True")
else:
    print("Percent_changetot: False")


# Print request count
print("Request count: ", count)
