import ccxt
import pandas as pd
import numpy as np
import os
from datetime import date, datetime, timezone, tzinfo
import time
import warnings


warnings.filterwarnings("ignore")


symbol = "ETH/BUSD"  # Binance
pos_size = 1
timeframe = "1m"


# API
account_binance = ccxt.binance({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": True,
    'options': {
        'defaultType': 'spot'
    }
})

fib_factor = 0.33 # Fib Factor for breakout confirmation, 0 ~ 1
ohlcvLB = account_binance.fetch_ohlcv(symbol, timeframe)
df = pd.DataFrame(ohlcvLB, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
if len(ohlcvLB):
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    # print(df)  # this is the dataframe

########################################
# bu_ob_boxes = np.zeros((5, 4), dtype=float)
# be_ob_boxes = np.zeros((5, 4), dtype=float)
bu_ob_boxes = []
be_ob_boxes = []
df['to_up'] = 0
df['to_down'] = 0
df['trend'] = 1
df['counter'] = 0
df['market'] = 1
df['zigzag'] = 0
df['zigzag_val'] = 0.0
h0=0
l0=0
h1=0
l1=0
zigzag_len = 9
last_trend_up_since = 0
cur_trend_up_since = 0
last_trend_down_since = 0
cur_trend_down_since = 0
high_points_arr = np.zeros(5, dtype=float)
high_index_arr = np.zeros(5)
low_points_arr = np.zeros(5, dtype=float)
low_index_arr = np.zeros(5)
last_h0 = 0
last_l0 = 0
hl_flag = 0
zigzag_points = []
l0is = np.zeros(zigzag_len)
h0is = np.zeros(zigzag_len)
def f_get_high(ind):
    if ind == 0:
        if zigzag_points[len(zigzag_points)-1][0] == 0:
            return [zigzag_points[len(zigzag_points)- 2][3],zigzag_points[len(zigzag_points) - 2][2]]
        else:
            return [zigzag_points[len(zigzag_points) - 1][3], zigzag_points[len(zigzag_points) - 1][2]]
    else:
        if zigzag_points[len(zigzag_points) - 1][0] == 0:
            return [zigzag_points[len(zigzag_points) - 2][3], zigzag_points[len(zigzag_points) - 2][2], zigzag_points[len(zigzag_points) - 2][1]]
        else:
            return [zigzag_points[len(zigzag_points) - 3][3], zigzag_points[len(zigzag_points) - 3][2],  zigzag_points[len(zigzag_points) - 3][1]]
    # return [high_points_arr[np.size(high_points_arr) - 1 - ind], high_index_arr[np.size(high_index_arr) - 1 - ind]]

def f_get_low(ind):
    if ind == 0:
        if zigzag_points[len(zigzag_points)-1][0] == 0:
            return [zigzag_points[len(zigzag_points)- 1][3],zigzag_points[len(zigzag_points)- 1][2]]
        else:
            return [zigzag_points[len(zigzag_points) - 2][3], zigzag_points[len(zigzag_points) - 2][2]]
    else:
        if zigzag_points[len(zigzag_points)-1][0] == 0:
            return [zigzag_points[len(zigzag_points)- 3][3],zigzag_points[len(zigzag_points)- 3][2], zigzag_points[len(zigzag_points)- 3][1]]
        else:
            return [zigzag_points[len(zigzag_points) - 4][3], zigzag_points[len(zigzag_points) - 4][2], zigzag_points[len(zigzag_points) - 4][1]]
    # return [low_points_arr[np.size(low_points_arr) - 1 - ind], low_index_arr[np.size(low_index_arr) - 1 - ind]]

temp = 0
for i in range(zigzag_len, len(df)):
    if df.high[i] >= df.high[(i-zigzag_len)+1:i].max():
        df.to_up[i] = 1
        last_trend_up_since = cur_trend_up_since
        cur_trend_up_since = i

    if df.low[i] <= df.low[(i-zigzag_len)+1:i].min():
        df.to_down[i] = 1
        last_trend_down_since = cur_trend_down_since
        cur_trend_down_since = i

    if df.trend[i-1] == 1 and df.to_down[i] == 1:
        df.trend[i] = -1
    elif df.trend[i-1] == -1 and df.to_up[i] == 1:
        df.trend[i] = 1
    else:
        df.trend[i] = df.trend[i-1]

    if df.trend[i] == 1 and df.trend[i-1] == -1:
        pp = (i-1)-last_trend_up_since
        sp = (i-pp)+1
        sp = i if pp < 1 else sp
        ep = i+1
        low_val = df.low[sp:ep].min()
        low_index = df.low[sp:ep].argmin()
        df.counter[i] = pp
        df.zigzag[sp+low_index] = -1
        df.zigzag_val[sp+low_index] = low_val
        low_points_arr = np.append(low_points_arr, low_val)
        low_index_arr = np.append(low_index_arr, low_index)
        zigzag_points.append([0,df.time[sp+low_index],sp+low_index,low_val])
        hl_flag = 0
        print("LOW:", df.time[sp + low_index], sp + low_index, low_val)
    if df.trend[i] == -1 and df.trend[i-1] == 1:
        pp = (i-1)-last_trend_down_since
        sp = (i-pp)+1
        sp = i if pp < 1 else sp
        ep = i+1
        high_val = df.high[sp:ep].max()
        high_index = df.high[sp:ep].argmax()
        df.counter[i] = pp
        df.zigzag[sp+high_index] = 1
        df.zigzag_val[sp+high_index] = high_val
        high_points_arr = np.append(high_points_arr, high_val)
        high_index_arr = np.append(high_index_arr, high_index)
        zigzag_points.append([1, df.time[sp+high_index],sp+high_index,high_val])
        hl_flag = 1
        print("HIGH:", df.time[sp + high_index], sp + high_index, high_val)

