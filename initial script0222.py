import pandas as pd
from binance.client import Client
import requests

# Initialize Binance API client
client = Client("api key", "secret api")


# Track number of requests
request_count = 0

# Get all USDT markets
markets = client.get_ticker()
request_count += 1

# Blacklist symbols
blacklist = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
usdt_markets = [market for market in markets if market['symbol'].endswith("USDT") and market['symbol'] not in blacklist]

#Add the BUSD list of symbols for check
list_busd = ["AERGOBUSD", "AGIXBUSD", "AMBBUSD"]
usdt_markets += [market for market in markets if market['symbol'] in list_busd and market['symbol'] not in blacklist]

# Get exchange information
exchange_info = client.get_exchange_info()
request_count += 1

# Extract symbols and statuses
symbols = [d['symbol'] for d in exchange_info['symbols']]
statuses = {d['symbol']: d['status'] for d in exchange_info['symbols']}

# Remove symbols that are not trading
usdt_markets = [market for market in usdt_markets if statuses[market['symbol']] == 'TRADING']



# Initialize empty dataframe
data = pd.DataFrame(columns=["symbol", "priceChangePercent", "volume"])

# Append symbol and 24 hour percent change to dataframe
for market in usdt_markets:
    symbol = market["symbol"]
    price_change = float(market["priceChangePercent"])
    volume = float(market["quoteVolume"])
    if volume > 1500000:
        data = pd.concat([data, pd.DataFrame({'symbol': symbol, 'priceChangePercent': price_change,'volume': "{:,.0f}".format(volume)}, index=[0])], ignore_index=True)
        request_count += 1

# Sort dataframe by 24 hour percent change
data.sort_values("priceChangePercent", inplace=True, ascending=False)

# Print the first 5 largest percent change
print(data.head(20))
# Print the number of requests made
print("Number of requests made: ", request_count)
