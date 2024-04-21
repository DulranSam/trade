import time
from binance.client import Client
import pandas as pd

# Binance API credentials
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

# Define symbols and parameters
symbol = 'BTCUSDT'
qty = 0.001
fast_ma_period = 50
slow_ma_period = 200

# Function to get historical data
def get_historical_data(symbol, interval, limit):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

# Function to check for crossover
def check_crossover(df, fast_period, slow_period):
    df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
    df['slow_ma'] = df['close'].rolling(window=slow_period).mean()
    df.dropna(inplace=True)
    if df['fast_ma'].iloc[-1] > df['slow_ma'].iloc[-1] and df['fast_ma'].iloc[-2] <= df['slow_ma'].iloc[-2]:
        return 'BUY'
    elif df['fast_ma'].iloc[-1] < df['slow_ma'].iloc[-1] and df['fast_ma'].iloc[-2] >= df['slow_ma'].iloc[-2]:
        return 'SELL'
    else:
        return 'HOLD'

# Main function
def main():
    while True:
        # Get current market time
        server_time = client.get_server_time()
        current_time = pd.to_datetime(server_time['serverTime'], unit='ms')

        # Get historical data
        df = get_historical_data(symbol, Client.KLINE_INTERVAL_1HOUR, 200)

        # Check for crossover
        signal = check_crossover(df, fast_ma_period, slow_ma_period)

        # Execute trade based on signal
        if signal == 'BUY':
            order = client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=qty
            )
            print("Buy order executed for {} {}".format(qty, symbol))
        elif signal == 'SELL':
            order = client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=qty
            )
            print("Sell order executed for {} {}".format(qty, symbol))
        else:
            print("No trade signal detected. Holding position.")

        # Sleep for 1 hour
        time.sleep(3600)

if __name__ == "__main__":
    main()
