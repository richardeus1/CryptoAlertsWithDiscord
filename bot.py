import yfinance as yf
import pandas as pd
import time
import requests
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from datetime import datetime

DISCORD_BOT_TOKEN = ""
DISCORD_CHANNEL_ID = ""
DISCORD_MESSAGE_ID = ""

TRACKED_COINS = ['BTC-USD', 'XRP-USD', 'AVAX-USD']
MAX_ROWS = 24

def fetch_data(symbol, period='30d', interval='1h'):
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def apply_indicators(df, ma_period=20, rsi_period=7):
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    df['SMA'] = SMAIndicator(close=close, window=ma_period).sma_indicator()
    df['RSI'] = RSIIndicator(close=close, window=rsi_period).rsi()

    # VWAP calculation for intraday
    # VWAP = (Typical Price * Volume).cumsum() / Volume.cumsum()
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()

    df.dropna(inplace=True)
    return df

def detect_hidden_divergence(df):
    """
    Detects hidden divergence using RSI over the last few candles.
    Looks for:
      - Higher low in price + lower low in RSI => hidden bullish
      - Lower high in price + higher high in RSI => hidden bearish
    """
    price = df['Close']
    rsi = df['RSI']

    if len(price) < 5:
        return None  # Not enough data

    # Use the last 5 bars
    p1, p2 = price.iloc[-5], price.iloc[-2]
    r1, r2 = rsi.iloc[-5], rsi.iloc[-2]

    # Ensure scalar:
    if isinstance(p1, pd.Series):
        p1 = p1.item()
    if isinstance(p2, pd.Series):
        p2 = p2.item()
    if isinstance(r1, pd.Series):
        r1 = r1.item()
    if isinstance(r2, pd.Series):
        r2 = r2.item()

    # Hidden Bullish: higher price low, lower RSI low
    if p2 > p1 and r2 < r1:
        return "HIDDEN_BULLISH"
    # Hidden Bearish: lower price high, higher RSI high
    elif p2 < p1 and r2 > r1:
        return "HIDDEN_BEARISH"

    return None

def generate_signal(df):
    last_close = df['Close'].iloc[-1]
    last_sma = df['SMA'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    last_vwap = df['VWAP'].iloc[-1]

    # Ensure scalar:
    if isinstance(last_close, pd.Series):
        last_close = last_close.item()
    if isinstance(last_sma, pd.Series):
        last_sma = last_sma.item()
    if isinstance(last_rsi, pd.Series):
        last_rsi = last_rsi.item()
    if isinstance(last_vwap, pd.Series):
        last_vwap = last_vwap.item()
    
    # Example simple logic incorporating VWAP:
    #if last_close > last_sma and last_rsi < 30 and last_close > last_vwap:
    #    return "BUY"
    #elif last_close < last_sma and last_rsi > 70 and last_close < last_vwap:
    #   return "SELL"
    #else:
    #    return "HOLD"
    
    #if last_close > last_sma and last_rsi < 30 and last_close > last_vwap:
    #    return "BUY"
    #elif last_close < last_sma and last_rsi > 70 and last_close < last_vwap:
    #    return "SELL"
    #else:
    #    return "HOLD"

    # Detect divergence
    divergence = detect_hidden_divergence(df)

    # Logic with all indicators
    if (
        #last_close > last_sma and
        #last_close > last_vwap and
        last_rsi < 35 and
        divergence == "HIDDEN_BULLISH"
    ):
        return "BUY"
    
    elif (
        last_rsi < 25 and 
        divergence != "HIDDEN_BULLISH" and
        last_close < last_vwap
    ):
        return "P SELL"

    elif (
        #last_close < last_sma and
        #last_close < last_vwap and
        last_rsi > 65 and
        divergence == "HIDDEN_BEARISH"
    ):
        return "SELL"
    
    elif (
        last_rsi > 75 and
        divergence != "HIDDEN_BEARISH" and
        last_close > last_vwap
    ):
        return "P BUY"

    elif (
        last_close > last_vwap and last_rsi < 30
    ):
        return "BUY os"

    elif (
        last_close < last_vwap and last_rsi > 70
    ):
        return "SELL ob"

    return "HOLD"

def build_table_row(name, price, rsi, sma, vwap, signal):
    # Defensive scalar conversion
    if isinstance(price, pd.Series):
        price = price.item()
    if isinstance(rsi, pd.Series):
        rsi = rsi.item()
    if isinstance(sma, pd.Series):
        sma = sma.item()
    if isinstance(vwap, pd.Series):
        vwap = vwap.item()

    now = time.strftime("%H:%M")
    return f"{now:<6} | {name:<7} | ${price:<9.2f} | {rsi:<6.2f} | {sma:<8.2f} | {vwap:<8.2f} | {signal:<4}"


def update_discord_message(table_lines):
    content = "```md\nTime   | Coin    | Price      | RSI    | SMA      | VWAP     | Signal\n" + "-"*70 + "\n"
    content += "\n".join(table_lines[-MAX_ROWS:]) + "\n```"

    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages/{DISCORD_MESSAGE_ID}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"content": content}
    response = requests.patch(url, headers=headers, json=data)

    if response.status_code not in (200, 204):
        print("Failed to update Discord message:", response.status_code, response.text)

# function to send new message if there is a change in signal column for the first 6 rows
def send_new_message(content):
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"content": f"Signal mismatch detected:\n```\n{content}\n```"}
    requests.post(url, headers=headers, json=data)

def main():
    new_rows = []
    HISTORY_FILE = "/pathwhereyourprojectislocatedonserver/history.log"

    for symbol in TRACKED_COINS:
        print(f"Checking {symbol}...")
        df = fetch_data(symbol)
        df = apply_indicators(df)
        signal = generate_signal(df)
        price = df['Close'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        sma = df['SMA'].iloc[-1]
        vwap = df['VWAP'].iloc[-1]

        new_rows.append(build_table_row(symbol, price, rsi, sma, vwap, signal))

    try:
        with open(HISTORY_FILE, "r") as f:
            existing_rows = f.read().strip().splitlines()
    except FileNotFoundError:
        existing_rows = []

    all_rows = (new_rows + existing_rows)[:MAX_ROWS]

    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(all_rows))

    update_discord_message(all_rows)

    # Check for signal mismatch in first 6 rows
    signals = [row.split("|")[-1].strip() for row in all_rows[:6] if '|' in row]
    if len(set(signals)) > 1:
        send_new_message("\n".join(all_rows[:6]))

if __name__ == "__main__":
    main()

